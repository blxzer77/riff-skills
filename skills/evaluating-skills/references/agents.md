# Agent adapters

Contents: [Adapters](#adapters) · [pi](#pi) · [claude-code](#claude-code) · [codex](#codex-unverified) · [command](#command-generic) · [Caveats](#caveats-for-every-agent) · [Adding an adapter](#adding-an-adapter)

The eval scripts drive agents only through `scripts/agents.py`. Pick one with
`--agent <name>`; `--agent-bin`, `--agent-home` and `--model` pass through.

## Adapters

| Adapter | Status | Skill installed at | Trigger detected when | Isolation |
|---|---|---|---|---|
| `pi` | Verified | `<workdir>/.riff-skill/<name>/`, passed with `--skill` | a `read` tool call opens `<name>/SKILL.md` | `--no-skills --no-context-files --no-extensions --no-prompt-templates --no-session` |
| `claude-code` | Verified (with a Claude Code-compatible binary) | `<workdir>/.claude/skills/<name>/` | the session transcript has a `Skill` call for `<name>` or a `Read` of `<name>/SKILL.md` | `--setting-sources project --strict-mcp-config` |
| `codex` | **Unverified** (written from the Codex CLI docs) | `<workdir>/.agents/skills/<name>/` | a `command_execution` item mentions `<name>/SKILL.md` | `exec --ephemeral --skip-git-repo-check --sandbox workspace-write` |
| `command` | Generic | `--skills-dir` (default `.agents/skills`) | stdout contains `<name>/SKILL.md` | whatever your command does |

Every run starts in a fresh git repository under `~/.cache/riff-skills/runs/`
(`--sandbox-root`), with only the skill under test installed and excluded from
git. The install is removed before outputs are copied.

### pi

- Prompt goes on stdin. JSON events come from `--mode json`. The final text is
  the last `turn_end` message that contains text, and tokens are the sum of
  `usage.totalTokens`.
- `--no-skills` turns off discovery, including `~/.agents/skills`, and leaves
  `--skill` paths active. That means the skill under test is the only one the
  agent sees.
- The grader and improver run with `--no-tools`.

### claude-code

- `-p --output-format json` prints only the final result. Tool calls are read
  from `<home>/projects/*/<session_id>.jsonl`, where `<home>` is
  `--agent-home`, otherwise `$CLAUDE_CONFIG_DIR`, otherwise `~/.claude`. When a
  compatible binary keeps its config somewhere else (for example `~/.cometix`),
  pass `--agent-home`.
- Without `--setting-sources project`, the user-level `CLAUDE.md` and user
  skills leak into every run. In testing, a user-level CLAUDE.md changed the
  reply language.
- `CLAUDECODE` is removed from the environment so runs can be launched from
  inside a session. Sessions are persisted so detection works, and the
  sandbox's project directory is deleted after parsing.
- Runs use `--permission-mode bypassPermissions`. That is acceptable only
  because the working directory is a throwaway sandbox.
- The grader runs with `--tools ""` and `--no-session-persistence`.

### codex (unverified)

- Not tested against a real install. Confirm these against your Codex version
  before trusting results:
  - the event names (`item.completed`, `turn.completed`);
  - that a skill load shows up as a command reading `SKILL.md`;
  - that `exec -` reads the prompt from stdin.
- Codex scans `.agents/skills` from the working directory up to the
  repository root, and also `~/.agents/skills`. User-level skills are not
  isolated.

### command (generic)

`--agent-cmd` is a shell-style template. Placeholders:

- `{prompt_file}`: the prompt is written there.
- `{workdir}`: the sandbox.
- `{skill_dir}`: the installed copy, or empty for baseline runs.

All of stdout is taken as the response, and tokens are not reported. Trigger
detection is a substring match, so it only works when the agent prints the
files it reads; otherwise every run looks like "not triggered".

```bash
run_triggers.py --skill skills/x --agent command \
  --agent-cmd "my-agent --quiet --prompt-file {prompt_file}" --skills-dir .agents/skills
```

## Caveats for every agent

- **Rate limits corrupt results silently.** An agent that hits HTTP 429 mid-task may
  still exit 0 with a half-done workdir. Adapters detect the agent's terminal error
  state (`RunResult.error`); `run_evals.py` retries such runs (`--retries`, backoff)
  and marks them `"error"` in `timing.json` if they keep failing, and `grade.py` /
  `aggregate.py` exclude them. Keep total concurrency (`--jobs` across everything
  you run at once) below what your model endpoint allows; running output and
  trigger evals in parallel is the usual way to exceed it.
- **Simple prompts rarely trigger skills.** Agents load a skill only when a task
  seems to need more than they already know. In testing, a Claude Code-compatible
  agent wrote a pirate greeting without loading a pirate-greeting skill; pi
  loaded it. Write substantive, realistic queries, and compare trigger rates
  between agents rather than assuming one agent's rate holds for another.
- Trigger runs on streaming adapters (`pi`, `codex`) stop as soon as the skill
  load is seen, so the response is incomplete by design. `claude-code` runs
  always finish.
- `timing.json` duration is wall time measured by the runner. Token counts
  follow each agent's own accounting (Claude Code counts cache reads), so
  compare tokens within one agent only.

## Adding an adapter

Subclass `Adapter` in `scripts/agents.py`, set `name`, `verified`,
`skills_subdir` and `streams_events`, implement `command`, `parse`, `complete`
(and `detect_line` if the agent streams events), then register it in
`ADAPTERS`. Verify it end to end on a toy skill before you mark it verified:

1. `run_evals.py --dry-run`
2. one `with_skill` and one `without_skill` run
3. `grade.py`, then `aggregate.py`
4. `run_triggers.py` with obvious positive and negative queries
