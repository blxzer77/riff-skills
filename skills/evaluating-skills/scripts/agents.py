"""Agent adapters: how to install a skill, launch an agent headless, and read its output.

Everything vendor-specific lives in this module. Scripts pick an adapter with
`get_adapter()` and only use the `Adapter` interface:

    extra = adapter.install(skill_dir | None, workdir)   # copy skill where the agent finds it
    argv, stdin = adapter.command(prompt, workdir, model, extra)
    proc = execute(argv, stdin, workdir, timeout, adapter.env())
    result = adapter.parse(proc.stdout, workdir)        # RunResult
    adapter.uninstall(workdir)
    text = adapter.complete(prompt, model)              # tool-less LLM call (grader, improver)

See ../references/agents.md for which adapters are verified and their caveats.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

from common import HarnessError, read_frontmatter

_SKILL_PATH = re.compile(r"""(?:^|[/\\\s"'`=])([^/\\\s"'`=]+)[/\\]SKILL\.md""")
_INSTALL_RECORD = "riff-installed.json"


@dataclass
class RunResult:
    response: str
    tokens: int | None
    transcript_lines: list[str]
    read_skill: set[str] = field(default_factory=set)
    # Set when the agent ended in an error state (API failure, rate limit) even if it
    # exited 0. Such runs say nothing about the skill and are retried, not graded.
    error: str | None = None


@dataclass
class Process:
    stdout: str
    stderr: str
    exit_code: int | None
    duration_ms: int
    timed_out: bool = False
    stopped_early: bool = False


def skill_names_in(text: str) -> set[str]:
    return set(_SKILL_PATH.findall(text))


def execute(argv, stdin_text, cwd, timeout, env=None, on_line=None) -> Process:
    """Run a command, enforcing a wall-clock timeout on its whole process group.

    `on_line(line) -> bool` sees each stdout line as it arrives; returning True
    stops the process early (used to end trigger runs once the outcome is known).
    """
    start = time.monotonic()
    try:
        proc = subprocess.Popen(
            argv, cwd=cwd, env=env, text=True, encoding="utf-8", errors="replace",
            stdin=subprocess.PIPE if stdin_text is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True,
        )
    except FileNotFoundError as exc:
        raise HarnessError(f"agent binary not found: {argv[0]}") from exc

    state = {"timed_out": False}

    def kill():
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            pass

    def on_timeout():
        state["timed_out"] = True
        kill()

    timer = threading.Timer(timeout, on_timeout)
    timer.start()
    err_chunks: list[str] = []
    err_thread = threading.Thread(target=lambda: err_chunks.append(proc.stderr.read()), daemon=True)
    err_thread.start()
    if stdin_text is not None:
        def feed():
            try:
                proc.stdin.write(stdin_text)
                proc.stdin.close()
            except (BrokenPipeError, OSError):
                pass
        threading.Thread(target=feed, daemon=True).start()

    out_lines, stopped = [], False
    for line in proc.stdout:
        out_lines.append(line)
        if on_line is not None and not stopped and on_line(line):
            stopped = True
            kill()
    proc.wait()
    timer.cancel()
    err_thread.join(timeout=5)
    return Process(
        stdout="".join(out_lines), stderr="".join(err_chunks),
        exit_code=None if (state["timed_out"] or stopped) else proc.returncode,
        duration_ms=int((time.monotonic() - start) * 1000),
        timed_out=state["timed_out"], stopped_early=stopped,
    )


class Adapter:
    """Base class. Subclasses set `name`, `verified`, `skills_subdir` and implement
    `command`, `parse` and `complete`."""

    name = ""
    verified = False
    skills_subdir = ".agents/skills"
    streams_events = False

    def __init__(self, bin: str | None = None, home: str | None = None):
        self.bin = bin

    def env(self) -> dict[str, str]:
        return dict(os.environ)

    def skill_args(self, installed: Path | None) -> list[str]:
        """Extra CLI args for a run; `installed` is the copied skill dir or None."""
        return []

    def install(self, skill_dir: Path | None, workdir: Path) -> list[str]:
        if skill_dir is None:
            return self.skill_args(None)
        name = read_frontmatter(skill_dir).get("name") or Path(skill_dir).name
        dest = workdir / self.skills_subdir / name
        if dest.exists():
            raise HarnessError(f"{dest} already exists in the fixture; refusing to overwrite")
        created, probe = [], dest
        while probe != workdir and not probe.exists():
            created.append(probe)
            probe = probe.parent
        shutil.copytree(skill_dir, dest, ignore=shutil.ignore_patterns("evals", "__pycache__"))
        git_dir = workdir / ".git"
        if git_dir.is_dir():
            rel = dest.relative_to(workdir).as_posix()
            (git_dir / "info").mkdir(exist_ok=True)
            with open(git_dir / "info" / "exclude", "a", encoding="utf-8") as fh:
                fh.write(f"/{rel}/\n")
            record = {"skill": str(dest), "created": [str(p) for p in created]}
            (git_dir / _INSTALL_RECORD).write_text(json.dumps(record), encoding="utf-8")
        return self.skill_args(dest)

    def uninstall(self, workdir: Path) -> None:
        record_path = workdir / ".git" / _INSTALL_RECORD
        if not record_path.is_file():
            return
        record = json.loads(record_path.read_text(encoding="utf-8"))
        shutil.rmtree(record["skill"], ignore_errors=True)
        for path in record["created"]:
            p = Path(path)
            if p.is_dir() and not any(p.iterdir()):
                p.rmdir()
        record_path.unlink()

    def command(self, prompt: str, workdir: Path, model: str | None,
                extra_args: list[str] | None = None) -> tuple[list[str], str | None]:
        raise NotImplementedError

    def detect_line(self, line: str) -> set[str]:
        """Skill names whose SKILL.md is loaded in one streamed stdout line."""
        return set()

    def parse(self, stdout: str, workdir: Path) -> RunResult:
        raise NotImplementedError

    def tool_log(self, transcript_lines: list[str]) -> str:
        """Condensed, readable list of tool calls and results from a saved transcript,
        so graders can check claims ("ran the tests, saw them fail") against actions.
        Returns "" when the adapter cannot extract one."""
        return ""

    def complete(self, prompt: str, model: str | None, timeout: int = 600) -> str:
        raise NotImplementedError

    def _complete_with(self, argv, stdin_text, timeout) -> Process:
        with tempfile.TemporaryDirectory(prefix="riff-complete-") as tmp:
            work = Path(tmp) / "work"
            work.mkdir()
            proc = execute(argv, stdin_text, work, timeout, self.env())
        if proc.exit_code != 0:
            tail = (proc.stderr or proc.stdout)[-800:]
            raise HarnessError(f"{self.name} completion failed (exit {proc.exit_code}, "
                               f"timed_out={proc.timed_out}): {tail}")
        return proc


def _json_lines(text: str):
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def _clip(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    half = limit // 2
    return f"{text[:half]}\n…[{len(text) - limit} chars omitted]…\n{text[-half:]}"


def _result_text(result) -> str:
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        content = result.get("content")
        if isinstance(content, list):
            return "\n".join(c.get("text", "") for c in content if isinstance(c, dict))
        return json.dumps(result)[:4000]
    if isinstance(result, list):
        return "\n".join(c.get("text", "") for c in result if isinstance(c, dict))
    return str(result)


def format_steps(steps: list[tuple[str, str, str, bool]], arg_limit=600, out_limit=1200) -> str:
    """steps: (tool, args_json, output, is_error) -> numbered plain-text log."""
    lines = []
    for i, (tool, args, output, is_error) in enumerate(steps, 1):
        flag = " [error]" if is_error else ""
        lines.append(f"{i}. {tool}{flag}: {_clip(args, arg_limit)}")
        if output.strip():
            lines.append("   → " + _clip(output, out_limit).replace("\n", "\n     "))
    return "\n".join(lines)


class PiAdapter(Adapter):
    name = "pi"
    verified = True
    skills_subdir = ".riff-skill"
    streams_events = True
    _base = ["-p", "--mode", "json", "--no-session", "--no-context-files",
             "--no-extensions", "--no-prompt-templates"]

    def __init__(self, bin=None, home=None):
        super().__init__(bin or "pi")

    def skill_args(self, installed):
        return ["--no-skills"] + (["--skill", str(installed)] if installed else [])

    def command(self, prompt, workdir, model, extra_args=None):
        argv = [self.bin, *self._base, *(extra_args or [])]
        if model:
            argv += ["--model", model]
        return argv, prompt

    def detect_line(self, line):
        line = line.strip()
        if '"tool_execution_start"' not in line:
            return set()
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            return set()
        if event.get("type") != "tool_execution_start":
            return set()
        return skill_names_in(json.dumps(event.get("args", {})))

    def parse(self, stdout, workdir):
        text, tokens, seen_usage, read, error = "", 0, False, set(), None
        for event in _json_lines(stdout):
            kind = event.get("type")
            if kind == "tool_execution_start":
                read |= skill_names_in(json.dumps(event.get("args", {})))
            elif kind == "turn_end":
                message = event.get("message") or {}
                usage = message.get("usage") or {}
                if isinstance(usage.get("totalTokens"), int):
                    tokens += usage["totalTokens"]
                    seen_usage = True
                parts = [c.get("text", "") for c in message.get("content") or []
                         if c.get("type") == "text"]
                if any(p.strip() for p in parts):
                    text = "".join(parts)
            elif kind == "agent_end":
                # The run's final state: an error here means the agent gave up mid-task.
                last = (event.get("messages") or [{}])[-1]
                error = (str(last.get("errorMessage") or "agent ended with an error")[:300]
                         if last.get("stopReason") == "error" else None)
        return RunResult(text, tokens if seen_usage else None, stdout.splitlines(), read, error)

    def tool_log(self, transcript_lines):
        starts, steps = {}, []
        for event in _json_lines("\n".join(transcript_lines)):
            kind = event.get("type")
            if kind == "tool_execution_start":
                starts[event.get("toolCallId")] = (event.get("toolName", "?"),
                                                    json.dumps(event.get("args", {})))
            elif kind == "tool_execution_end":
                tool, args = starts.pop(event.get("toolCallId"), (event.get("toolName", "?"), ""))
                steps.append((tool, args, _result_text(event.get("result")),
                              bool(event.get("isError"))))
        steps += [(tool, args, "(no result recorded)", False) for tool, args in starts.values()]
        return format_steps(steps)

    def complete(self, prompt, model, timeout=600):
        argv = [self.bin, *self._base, "--no-skills", "--no-tools"]
        if model:
            argv += ["--model", model]
        proc = self._complete_with(argv, prompt, timeout)
        return self.parse(proc.stdout, Path(".")).response


class ClaudeCodeAdapter(Adapter):
    """Claude Code and CLI-compatible binaries. Tool calls are read from the session
    transcript, because `-p --output-format json` prints only the final result."""

    name = "claude-code"
    verified = True
    skills_subdir = ".claude/skills"
    _base = ["-p", "--output-format", "json", "--setting-sources", "project",
             "--strict-mcp-config"]

    def __init__(self, bin=None, home=None):
        super().__init__(bin or "claude")
        self.home_override = home

    @property
    def home(self) -> Path:
        if self.home_override:
            return Path(self.home_override).expanduser()
        if os.environ.get("CLAUDE_CONFIG_DIR"):
            return Path(os.environ["CLAUDE_CONFIG_DIR"]).expanduser()
        return Path.home() / ".claude"

    def env(self):
        env = dict(os.environ)
        env.pop("CLAUDECODE", None)  # allow launching from inside another session
        if self.home_override:
            env["CLAUDE_CONFIG_DIR"] = str(self.home)
        return env

    def command(self, prompt, workdir, model, extra_args=None):
        argv = [self.bin, *self._base, "--permission-mode", "bypassPermissions",
                *(extra_args or [])]
        if model:
            argv += ["--model", model]
        return argv, prompt

    @staticmethod
    def _result(stdout):
        for line in reversed(stdout.strip().splitlines()):
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and ("result" in obj or "session_id" in obj):
                return obj
        return {}

    def _transcript(self, session_id, workdir):
        projects = self.home / "projects"
        if session_id:
            matches = sorted(projects.glob(f"*/{session_id}.jsonl"))
            if matches:
                return matches[0]
        # Timed-out runs print nothing; the sandbox id is unique and part of the project dir name.
        matches = sorted(projects.glob(f"*{workdir.parent.name}*/*.jsonl"), key=os.path.getmtime)
        return matches[-1] if matches else None

    def parse(self, stdout, workdir):
        obj = self._result(stdout)
        usage = obj.get("usage") or {}
        keys = ("input_tokens", "output_tokens", "cache_creation_input_tokens",
                "cache_read_input_tokens")
        counts = [usage[k] for k in keys if isinstance(usage.get(k), int)]
        tokens = sum(counts) if counts else None
        response = obj.get("result") if isinstance(obj.get("result"), str) else ""
        error = None
        if obj.get("is_error") or (obj.get("subtype") not in (None, "success")):
            error = f"{obj.get('subtype') or 'error'}: {response[:300]}"
        path = self._transcript(obj.get("session_id"), Path(workdir))
        if path is None:
            return RunResult(response, tokens, stdout.splitlines(), set(), error)
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        read = set()
        for entry in _json_lines("\n".join(lines)):
            content = (entry.get("message") or {}).get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict) or block.get("type") != "tool_use":
                    continue
                payload = block.get("input") or {}
                if block.get("name") == "Skill" and isinstance(payload.get("skill"), str):
                    read.add(payload["skill"].split(":")[-1])
                else:
                    read |= skill_names_in(json.dumps(payload))
        self._remove_session(path, Path(workdir))
        return RunResult(response, tokens, lines, read, error)

    def tool_log(self, transcript_lines):
        calls, steps = {}, []
        for entry in _json_lines("\n".join(transcript_lines)):
            content = (entry.get("message") or {}).get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_use":
                    calls[block.get("id")] = (block.get("name", "?"),
                                              json.dumps(block.get("input", {})))
                elif block.get("type") == "tool_result":
                    tool, args = calls.pop(block.get("tool_use_id"), ("?", ""))
                    steps.append((tool, args, _result_text(block.get("content")),
                                  bool(block.get("is_error"))))
        steps += [(tool, args, "(no result recorded)", False) for tool, args in calls.values()]
        return format_steps(steps)

    @staticmethod
    def _remove_session(path: Path, workdir: Path) -> None:
        # The agent stores sessions under its config home; delete only the project dir
        # created for this sandbox (its name embeds the unique sandbox id).
        project = path.parent
        if workdir.parent.name and workdir.parent.name in project.name:
            shutil.rmtree(project, ignore_errors=True)

    def complete(self, prompt, model, timeout=600):
        argv = [self.bin, *self._base, "--no-session-persistence", "--tools", ""]
        if model:
            argv += ["--model", model]
        proc = self._complete_with(argv, prompt, timeout)
        return self._result(proc.stdout).get("result") or ""


class CodexAdapter(Adapter):
    """UNVERIFIED: written from the Codex CLI docs; not run on a real install yet."""

    name = "codex"
    verified = False
    skills_subdir = ".agents/skills"
    streams_events = True
    _base = ["exec", "--json", "--ephemeral", "--skip-git-repo-check"]

    def __init__(self, bin=None, home=None):
        super().__init__(bin or "codex")

    def command(self, prompt, workdir, model, extra_args=None):
        argv = [self.bin, *self._base, "--sandbox", "workspace-write", *(extra_args or [])]
        if model:
            argv += ["-m", model]
        return argv + ["-"], prompt

    @staticmethod
    def _item_reads(event) -> set[str]:
        item = event.get("item") or {}
        if item.get("type") == "command_execution":
            return skill_names_in(str(item.get("command", "")))
        return set()

    def detect_line(self, line):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            return set()
        return self._item_reads(event) if str(event.get("type", "")).startswith("item.") else set()

    def parse(self, stdout, workdir):
        text, tokens, seen_usage, read, error = "", 0, False, set(), None
        for event in _json_lines(stdout):
            kind = str(event.get("type", ""))
            if kind.startswith("item."):
                read |= self._item_reads(event)
                item = event.get("item") or {}
                if kind == "item.completed" and item.get("type") == "agent_message":
                    text = item.get("text", "")
            elif kind == "turn.completed":
                usage = event.get("usage") or {}
                parts = [usage.get(k) for k in ("input_tokens", "output_tokens")]
                if all(isinstance(p, int) for p in parts):
                    tokens += sum(parts)
                    seen_usage = True
            elif kind in ("turn.failed", "error"):
                error = str(event.get("error") or event.get("message") or kind)[:300]
        return RunResult(text, tokens if seen_usage else None, stdout.splitlines(), read, error)

    def tool_log(self, transcript_lines):
        steps = []
        for event in _json_lines("\n".join(transcript_lines)):
            item = event.get("item") or {}
            if event.get("type") == "item.completed" and item.get("type") == "command_execution":
                steps.append(("command", str(item.get("command", "")),
                              str(item.get("aggregated_output", "")),
                              item.get("exit_code") not in (0, None)))
        return format_steps(steps)

    def complete(self, prompt, model, timeout=600):
        argv = [self.bin, *self._base, "--sandbox", "read-only"]
        if model:
            argv += ["-m", model]
        proc = self._complete_with(argv + ["-"], prompt, timeout)
        return self.parse(proc.stdout, Path(".")).response


class CommandAdapter(Adapter):
    """Generic adapter for any CLI: `--agent-cmd` is a template with {prompt_file},
    {workdir} and {skill_dir}; stdout is the response; trigger detection is a
    substring match on `<name>/SKILL.md` in stdout."""

    name = "command"
    verified = False

    def __init__(self, bin=None, home=None, cmd=None, skills_dir=None):
        super().__init__(bin)
        if not cmd:
            raise HarnessError("--agent command requires --agent-cmd")
        self.template = shlex.split(cmd)
        self.skills_subdir = skills_dir or ".agents/skills"

    def skill_args(self, installed):
        return [str(installed)] if installed else []

    def command(self, prompt, workdir, model, extra_args=None):
        prompt_file = Path(workdir).parent / "prompt.md"
        if prompt_file.parent.is_dir():  # absent during --dry-run
            prompt_file.write_text(prompt, encoding="utf-8")
        skill_dir = (extra_args or [""])[0]
        values = {"prompt_file": str(prompt_file), "workdir": str(workdir), "skill_dir": skill_dir}
        return [token.format(**values) for token in self.template], None

    def parse(self, stdout, workdir):
        return RunResult(stdout.strip(), None, stdout.splitlines(), skill_names_in(stdout))

    def complete(self, prompt, model, timeout=600):
        with tempfile.TemporaryDirectory(prefix="riff-complete-") as tmp:
            work = Path(tmp) / "work"
            work.mkdir()
            argv, _ = self.command(prompt, work, model, [])
            proc = execute(argv, None, work, timeout, self.env())
        if proc.exit_code != 0:
            raise HarnessError(f"command completion failed (exit {proc.exit_code})")
        return proc.stdout.strip()


ADAPTERS = {cls.name: cls for cls in (PiAdapter, ClaudeCodeAdapter, CodexAdapter, CommandAdapter)}


def get_adapter(name: str, bin: str | None = None, home: str | None = None,
                cmd: str | None = None, skills_dir: str | None = None) -> Adapter:
    if name not in ADAPTERS:
        raise HarnessError(f"unknown agent '{name}'; choose from {', '.join(ADAPTERS)}")
    if name == "command":
        return CommandAdapter(bin, home, cmd=cmd, skills_dir=skills_dir)
    return ADAPTERS[name](bin, home)


def add_agent_args(parser, required: bool = True) -> None:
    group = parser.add_argument_group("agent")
    group.add_argument("--agent", required=required, choices=sorted(ADAPTERS),
                       help="agent adapter (see references/agents.md)")
    group.add_argument("--agent-bin", help="agent executable (default depends on adapter)")
    group.add_argument("--agent-home", help="agent config home, e.g. for transcript lookup")
    group.add_argument("--agent-cmd", help="command template for --agent command")
    group.add_argument("--skills-dir", help="install dir relative to workdir for --agent command")
    group.add_argument("--model", help="model passed through to the agent")


def adapter_from_args(args) -> Adapter:
    return get_adapter(args.agent, bin=args.agent_bin, home=args.agent_home,
                       cmd=args.agent_cmd, skills_dir=args.skills_dir)
