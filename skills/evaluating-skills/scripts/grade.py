#!/usr/bin/env python3
"""Grade every run in an iteration against the skill's current assertions.

Script assertions (objects with "script") run mechanically; string assertions go
to an LLM grader driven by references/grader.md through the chosen agent adapter.
Writes run-*/grading.json per references/schemas.md.

Example:
    grade.py --iteration .workspace/writing-tests/iteration-1 \\
             --skill skills/writing-tests --agent pi
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from agents import add_agent_args, adapter_from_args, get_adapter
from common import (HarnessError, die, eval_dirname, load_evals, normalize_assertions,
                    read_json, truncate, write_json)

LIMIT = 60_000
SCRIPT_TIMEOUT = 300
GRADER_ATTEMPTS = 3
DEFAULT_GRADER = Path(__file__).resolve().parent.parent / "references" / "grader.md"


def run_script(spec: dict, skill_dir: Path, run_dir: Path, fixture: Path) -> dict:
    script = (skill_dir / spec["script"]).resolve()
    if not script.is_file():
        return {"text": spec["text"], "passed": False, "method": "script",
                "evidence": f"script not found: {spec['script']}"}
    if os.access(script, os.X_OK):
        argv = [str(script)]
    elif script.suffix == ".py":
        argv = [sys.executable, str(script)]
    elif script.suffix == ".sh":
        argv = ["bash", str(script)]
    else:
        return {"text": spec["text"], "passed": False, "method": "script",
                "evidence": f"script is not executable and has no known interpreter: {script.name}"}
    outputs = run_dir / "outputs"
    env = dict(os.environ, EVAL_WORKDIR=str(outputs / "workdir"), EVAL_FIXTURE=str(fixture),
               EVAL_RESPONSE=str(outputs / "response.md"))
    try:
        proc = subprocess.run(argv, cwd=run_dir, env=env, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=SCRIPT_TIMEOUT)
        output = (proc.stdout + proc.stderr).strip()
        passed = proc.returncode == 0
        evidence = output[-2000:] or f"exit code {proc.returncode}"
    except subprocess.TimeoutExpired:
        passed, evidence = False, f"script timed out after {SCRIPT_TIMEOUT}s"
    return {"text": spec["text"], "passed": passed, "evidence": evidence, "method": "script"}


def _close_brackets(text: str) -> str:
    """Append the closers a JSON document is missing at its end. Models sometimes drop
    the final brace(s) of an otherwise complete object; nothing else is repaired."""
    stack, in_str, escaped = [], False, False
    for ch in text:
        if in_str:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch in "{[":
            stack.append("}" if ch == "{" else "]")
        elif ch in "}]" and stack:
            stack.pop()
    return text if in_str else text + "".join(reversed(stack))


def extract_json(text: str) -> dict | None:
    decoder = json.JSONDecoder()
    for i, char in enumerate(text):
        if char != "{":
            continue
        for candidate in (text[i:], _close_brackets(text[i:].rstrip())):
            try:
                obj, _ = decoder.raw_decode(candidate)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and isinstance(obj.get("assertion_results"), list):
                return obj
    return None


def section(title: str, body: str) -> str:
    body, cut = truncate(body, LIMIT)
    note = f"\n[truncated to the first {LIMIT} characters]" if cut else ""
    return f"## {title}\n\n{body or '(empty)'}{note}\n"


def tool_log(run_adapter, outputs: Path) -> str:
    transcript = outputs / "transcript.jsonl"
    if run_adapter is None or not transcript.is_file():
        return ""
    lines = transcript.read_text(encoding="utf-8", errors="replace").splitlines()
    return run_adapter.tool_log(lines)


def grader_prompt(instructions: str, meta: dict, texts: list[str], run_dir: Path,
                  run_adapter=None) -> str:
    outputs = run_dir / "outputs"
    response = (outputs / "response.md").read_text(encoding="utf-8", errors="replace") \
        if (outputs / "response.md").is_file() else ""
    patch = (outputs / "changes.patch").read_text(encoding="utf-8", errors="replace") \
        if (outputs / "changes.patch").is_file() else ""
    actions = tool_log(run_adapter, outputs)
    workdir = outputs / "workdir"
    files = sorted(p.relative_to(workdir).as_posix() for p in workdir.rglob("*") if p.is_file()) \
        if workdir.is_dir() else []
    numbered = "\n".join(f"{i}. {t}" for i, t in enumerate(texts, 1))
    return "\n".join([
        instructions.strip(), "",
        "# Material to grade", "",
        section("Task prompt given to the agent", meta.get("prompt", "")),
        section("Expected output", meta.get("expected_output", "")),
        section("Assertions to grade", numbered),
        section("Agent's final response (outputs/response.md)", response),
        section("Tool calls the agent made, in order, with clipped results", actions
                or "(not available for this agent)"),
        section("Changes the agent made to the working directory (outputs/changes.patch)", patch),
        section("Files in the final working directory", "\n".join(files[:300])),
        "Reply with one JSON object and nothing else, shaped like:",
        '{"assertion_results": [{"text": "<assertion text verbatim>", "passed": true, '
        '"evidence": "<quote or concrete reference>"}], "claims": [], '
        '"eval_feedback": {"suggestions": [], "overall": ""}}',
        "Include every assertion exactly once, in the order given.",
    ])


def grade_llm(adapter, model, instructions, meta, specs, run_dir,
              run_adapter=None) -> tuple[list[dict], dict]:
    texts = [s["text"] for s in specs]
    prompt = grader_prompt(instructions, meta, texts, run_dir, run_adapter)
    parsed, error, raw = None, "", ""
    for _ in range(GRADER_ATTEMPTS):
        try:
            raw = adapter.complete(prompt, model)
            parsed = extract_json(raw)
            error = "" if parsed else "no JSON object with assertion_results in reply"
        except HarnessError as exc:
            error, parsed = str(exc), None
        if parsed:
            break
    if not parsed:
        # Keep the last reply so a grading failure can be told apart from a bad run.
        (run_dir / "grader-raw.txt").write_text(f"{error}\n\n{raw}", encoding="utf-8")
        evidence = f"grader output unparseable after {GRADER_ATTEMPTS} attempts ({error[:300]}); " \
                   "see grader-raw.txt"
        return [{"text": t, "passed": False, "evidence": evidence, "method": "llm"}
                for t in texts], {}
    by_text = {r.get("text"): r for r in parsed["assertion_results"] if isinstance(r, dict)}
    ordered = [r for r in parsed["assertion_results"] if isinstance(r, dict)]
    results = []
    for i, text in enumerate(texts):
        verdict = by_text.get(text) or (ordered[i] if i < len(ordered) else None)
        if verdict is None:
            results.append({"text": text, "passed": False, "method": "llm",
                            "evidence": "grader returned no verdict for this assertion"})
            continue
        results.append({"text": text, "passed": verdict.get("passed") is True,
                        "evidence": str(verdict.get("evidence", "")), "method": "llm"})
    extras = {k: parsed[k] for k in ("claims", "eval_feedback") if k in parsed}
    return results, extras


def grade_run(run_dir, eval_dir, specs, skill_dir, adapter, model, instructions, only_scripts,
              run_adapter=None):
    meta = read_json(eval_dir / "eval_metadata.json")
    fixture = eval_dir / "fixture"
    results: dict[int, dict] = {}
    llm_specs = []
    for i, spec in enumerate(specs):
        if spec.get("script"):
            results[i] = run_script(spec, skill_dir, run_dir, fixture)
        elif not only_scripts:
            llm_specs.append((i, spec))
    extras = {}
    if llm_specs:
        llm_results, extras = grade_llm(adapter, model, instructions, meta,
                                        [s for _, s in llm_specs], run_dir, run_adapter)
        for (i, _), result in zip(llm_specs, llm_results):
            results[i] = result
    graded = [results[i] for i in sorted(results)]
    passed = sum(1 for r in graded if r["passed"])
    data = {"assertion_results": graded,
            "summary": {"passed": passed, "failed": len(graded) - passed, "total": len(graded),
                        "pass_rate": round(passed / len(graded), 4) if graded else None}}
    data.update(extras)
    write_json(run_dir / "grading.json", data)
    return data["summary"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--iteration", required=True, type=Path, help="iteration-N directory")
    parser.add_argument("--skill", required=True, type=Path,
                        help="skill whose evals/evals.json holds the assertions")
    parser.add_argument("--only-scripts", action="store_true",
                        help="grade script assertions only (skip LLM-graded ones)")
    parser.add_argument("--grader-instructions", type=Path, default=DEFAULT_GRADER,
                        help="grader instructions file (default: references/grader.md)")
    parser.add_argument("--jobs", type=int, default=2, help="parallel grading runs")
    add_agent_args(parser, required=False)
    args = parser.parse_args()

    iter_dir = args.iteration.resolve()
    skill_dir = args.skill.resolve()
    if not iter_dir.is_dir():
        die(f"no such iteration directory: {iter_dir}")
    try:
        evals = {eval_dirname(e): e for e in load_evals(skill_dir)}
    except HarnessError as exc:
        die(str(exc))

    work = []
    for eval_dir in sorted(iter_dir.glob("eval-*")):
        if eval_dir.name not in evals:
            print(f"warning: {eval_dir.name} is not in evals.json; skipped", file=sys.stderr)
            continue
        try:
            specs = normalize_assertions(evals[eval_dir.name].get("assertions"))
        except HarnessError as exc:
            die(f"{eval_dir.name}: {exc}")
        meta_path = eval_dir / "eval_metadata.json"
        meta = read_json(meta_path)
        meta["assertions"] = specs
        write_json(meta_path, meta)
        for run_dir in sorted(eval_dir.glob("*/run-*")):
            timing = run_dir / "timing.json"
            if timing.is_file() and read_json(timing).get("error"):
                print(f"warning: {run_dir.relative_to(iter_dir)} ended in an agent error; "
                      "not graded (re-run it)", file=sys.stderr)
                (run_dir / "grading.json").unlink(missing_ok=True)
                continue
            work.append((run_dir, eval_dir, specs))
    if not work:
        die(f"no runs found under {iter_dir}")

    needs_llm = not args.only_scripts and any(
        not s.get("script") for _, _, specs in work for s in specs)
    adapter, instructions = None, ""
    if needs_llm:
        if not args.agent:
            die("string assertions need an LLM grader: pass --agent (or use --only-scripts)")
        if not args.grader_instructions.is_file():
            die(f"grader instructions not found: {args.grader_instructions}")
        instructions = args.grader_instructions.read_text(encoding="utf-8")
        try:
            adapter = adapter_from_args(args)
        except HarnessError as exc:
            die(str(exc))

    # The transcripts were written by the agent that ran the evals, which may differ
    # from the grading agent; parse them with that agent's adapter.
    run_adapter = None
    config_path = iter_dir / "run_config.json"
    if config_path.is_file():
        try:
            run_adapter = get_adapter(read_json(config_path).get("agent", ""))
        except HarnessError:
            run_adapter = None

    rows = []
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        futures = {pool.submit(grade_run, run_dir, eval_dir, specs, skill_dir, adapter,
                               args.model, instructions, args.only_scripts,
                               run_adapter): run_dir
                   for run_dir, eval_dir, specs in work}
        for future in as_completed(futures):
            run_dir = futures[future]
            rows.append((run_dir.relative_to(iter_dir).as_posix(), future.result()))

    for rel, summary in sorted(rows):
        rate = "-" if summary["pass_rate"] is None else f"{summary['pass_rate']:.2f}"
        print(f"{rel:60} {summary['passed']}/{summary['total']}  pass_rate={rate}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
