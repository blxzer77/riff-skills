#!/usr/bin/env python3
"""Measure how often a skill's description makes the agent load the skill.

Each query runs `--runs` times in an empty sandbox where only this skill is
installed. A run counts as triggered when the agent loads the skill's SKILL.md.
Streaming adapters stop a run as soon as the outcome is known.

Example:
    run_triggers.py --skill skills/writing-tests --agent pi --set train
    run_triggers.py --skill skills/writing-tests --agent pi --set validation \\
                    --description-file candidate.txt
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from agents import add_agent_args, adapter_from_args, execute
from common import HarnessError, die, read_frontmatter, read_json, replace_description, write_json
from sandbox import DEFAULT_ROOT, sandbox


def run_query(query: str, skill_dir: Path, name: str, adapter, model, timeout, root):
    with sandbox(root) as workdir:
        extra = adapter.install(skill_dir, workdir)
        argv, stdin_text = adapter.command(query, workdir, model, extra)

        def stop_when_known(line: str) -> bool:
            return name in adapter.detect_line(line)

        proc = execute(argv, stdin_text, workdir, timeout, adapter.env(),
                       on_line=stop_when_known if adapter.streams_events else None)
        result = adapter.parse(proc.stdout, workdir)
        adapter.uninstall(workdir)
    triggered = name in result.read_skill
    # A run that errored before the agent decided anything is no evidence either way.
    failed = not triggered and not proc.stopped_early and (
        proc.exit_code != 0 or result.error is not None)
    return triggered, failed, proc, result.error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skill", required=True, type=Path, help="skill directory")
    parser.add_argument("--queries", type=Path,
                        help="default: <skill>/evals/trigger-queries.json")
    parser.add_argument("--set", choices=["train", "validation", "all"], default="train")
    parser.add_argument("--description-file", type=Path,
                        help="test this description instead of the one in SKILL.md")
    parser.add_argument("--runs", type=int, default=3, help="runs per query")
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=180, help="seconds per run")
    parser.add_argument("--workspace", type=Path, help="default: .workspace/<skill-name>")
    parser.add_argument("--sandbox-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--dry-run", action="store_true", help="print the plan and exit")
    add_agent_args(parser)
    args = parser.parse_args()

    skill_dir = args.skill.resolve()
    try:
        meta = read_frontmatter(skill_dir)
        adapter = adapter_from_args(args)
    except HarnessError as exc:
        die(str(exc))
    name = meta.get("name") or skill_dir.name
    queries_path = args.queries or skill_dir / "evals" / "trigger-queries.json"
    if not queries_path.is_file():
        die(f"missing {queries_path}")
    queries = read_json(queries_path)
    if args.set != "all":
        missing = [q for q in queries if q.get("set") not in ("train", "validation")]
        if missing:
            die(f"{len(missing)} queries have no 'set'; run split_queries.py first")
        queries = [q for q in queries if q["set"] == args.set]
    if not queries:
        die(f"no queries in set '{args.set}'")

    description = meta.get("description", "")
    if args.description_file:
        description = args.description_file.read_text(encoding="utf-8").strip()
        if not description or len(description) > 1024:
            die(f"candidate description must be 1-1024 characters (got {len(description)})")

    if args.dry_run:
        argv, stdin_text = adapter.command("<query>", Path("<sandbox>/work"), args.model,
                                           ["<skill-args>"])
        print(f"{len(queries)} queries x {args.runs} runs, set={args.set}, agent={adapter.name}")
        print(f"argv: {argv}{'  (query on stdin)' if stdin_text is not None else ''}")
        print(f"description ({len(description)} chars): {description}")
        return 0

    with tempfile.TemporaryDirectory(prefix="riff-trigger-skill-") as tmp:
        tested = Path(tmp) / skill_dir.name
        shutil.copytree(skill_dir, tested, ignore=shutil.ignore_patterns("evals", "__pycache__"))
        if args.description_file:
            replace_description(tested / "SKILL.md", description)

        counts = {i: {"triggers": 0, "runs": 0} for i in range(len(queries))}
        infra_errors = 0
        with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
            futures = {pool.submit(run_query, q["query"], tested, name, adapter, args.model,
                                   args.timeout, args.sandbox_root): i
                       for i, q in enumerate(queries) for _ in range(args.runs)}
            for future in as_completed(futures):
                i = futures[future]
                try:
                    triggered, failed, proc, agent_error = future.result()
                except HarnessError as exc:
                    infra_errors += 1
                    print(f"error: {exc}", file=sys.stderr)
                    continue
                if failed:
                    infra_errors += 1
                    detail = agent_error or proc.stderr.strip()[-300:]
                    print(f"error: query {i} exit={proc.exit_code} timed_out={proc.timed_out}: "
                          f"{detail[:300]}", file=sys.stderr)
                    continue
                counts[i]["runs"] += 1
                counts[i]["triggers"] += int(triggered)

    if all(c["runs"] == 0 for c in counts.values()):
        die("every run failed; no results written", code=2)

    results = []
    for i, q in enumerate(queries):
        runs, triggers = counts[i]["runs"], counts[i]["triggers"]
        rate = triggers / runs if runs else None
        if rate is None:
            passed = None
        elif q["should_trigger"]:
            passed = rate >= args.threshold
        else:
            passed = rate < args.threshold
        results.append({"query": q["query"], "should_trigger": q["should_trigger"],
                        "set": q.get("set"), "triggers": triggers, "runs": runs,
                        "trigger_rate": None if rate is None else round(rate, 2),
                        "passed": passed})
    fn = sum(1 for r in results if r["should_trigger"] and r["passed"] is False)
    fp = sum(1 for r in results if not r["should_trigger"] and r["passed"] is False)
    passed = sum(1 for r in results if r["passed"])
    summary = {"total": len(results), "passed": passed, "failed": fn + fp,
               "false_negatives": fn, "false_positives": fp}
    errored = sum(1 for r in results if r["passed"] is None)
    if errored:
        summary["errored"] = errored
    report = {"skill_name": name, "description": description, "agent": adapter.name,
              "model": args.model, "set": args.set, "runs_per_query": args.runs,
              "threshold": args.threshold, "results": results, "summary": summary}
    workspace = (args.workspace or Path(".workspace") / name).resolve()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out = workspace / "triggers" / f"{stamp}-{args.set}.json"
    write_json(out, report)

    for r in results:
        mark = {True: "PASS", False: "FAIL", None: "ERR "}[r["passed"]]
        want = "trigger" if r["should_trigger"] else "no-trigger"
        print(f"{mark}  {want:10} {r['triggers']}/{r['runs']}  {r['query'][:90]}")
    s = report["summary"]
    print(f"passed {s['passed']}/{s['total']}  false_negatives={s['false_negatives']}  "
          f"false_positives={s['false_positives']}"
          + (f"  errored={s['errored']}" if errored else "") + f"\nresults: {out}")
    return 2 if infra_errors else 0


if __name__ == "__main__":
    sys.exit(main())
