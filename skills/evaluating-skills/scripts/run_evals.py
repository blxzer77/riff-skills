#!/usr/bin/env python3
"""Run a skill's output evals with and without the skill (or against a snapshot).

Each eval x configuration x repetition runs in a fresh git-initialized sandbox
outside the repository, and its outputs land in the workspace layout described
in references/schemas.md:

    <workspace>/iteration-N/eval-<name>/<configuration>/run-<k>/{outputs/,timing.json}

Example:
    run_evals.py --skill skills/writing-tests --agent pi --runs 1
    run_evals.py --skill skills/writing-tests --agent pi --baseline old_skill
"""

from __future__ import annotations

import argparse
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from agents import add_agent_args, adapter_from_args, execute
from common import (HarnessError, die, eval_dirname, is_within, load_evals,
                    normalize_assertions, skill_name, utc_now, write_json)
from sandbox import DEFAULT_ROOT, copy_fixture, diff_against_fixture, sandbox

RETRY_BACKOFF_SECONDS = 30


def next_iteration(workspace: Path) -> int:
    taken = [int(p.name.split("-", 1)[1]) for p in workspace.glob("iteration-*")
             if p.name.split("-", 1)[1].isdigit()]
    return max(taken, default=0) + 1


def attempt(job, adapter, model, timeout, sandbox_root, outputs):
    """One agent run in a fresh sandbox; writes outputs/ and returns (proc, result)."""
    if outputs.exists():
        shutil.rmtree(outputs)
    outputs.mkdir(parents=True)
    with sandbox(sandbox_root, job["fixture"]) as workdir:
        extra = adapter.install(job["skill"], workdir)
        argv, stdin_text = adapter.command(job["prompt"], workdir, model, extra)
        proc = execute(argv, stdin_text, workdir, timeout, adapter.env())
        result = adapter.parse(proc.stdout, workdir)
        adapter.uninstall(workdir)
        (outputs / "response.md").write_text(result.response, encoding="utf-8")
        (outputs / "transcript.jsonl").write_text("\n".join(result.transcript_lines) + "\n",
                                                  encoding="utf-8")
        (outputs / "changes.patch").write_text(diff_against_fixture(workdir), encoding="utf-8")
        if proc.stderr.strip():
            (outputs / "agent-stderr.log").write_text(proc.stderr[-20000:], encoding="utf-8")
        shutil.copytree(workdir, outputs / "workdir", ignore=shutil.ignore_patterns(".git"))
    return proc, result


def run_one(job: dict, adapter, model, timeout, sandbox_root, retries) -> dict:
    run_dir: Path = job["run_dir"]
    for n in range(retries + 1):
        if n:
            time.sleep(RETRY_BACKOFF_SECONDS * n)
        proc, result = attempt(job, adapter, model, timeout, sandbox_root, run_dir / "outputs")
        if result.error is None:
            break
        print(f"agent error in {run_dir} (attempt {n + 1}/{retries + 1}): {result.error[:160]}",
              file=sys.stderr)
    timing = {"total_tokens": result.tokens, "duration_ms": proc.duration_ms,
              "agent": adapter.name, "model": model, "exit_code": proc.exit_code}
    if proc.timed_out:
        timing["timed_out"] = True
    if result.error is not None:
        timing["error"] = result.error
    write_json(run_dir / "timing.json", timing)
    return {"run": run_dir, "exit_code": proc.exit_code, "timed_out": proc.timed_out,
            "seconds": proc.duration_ms / 1000, "tokens": result.tokens,
            "read_skill": sorted(result.read_skill), "error": result.error}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skill", required=True, type=Path, help="skill directory")
    parser.add_argument("--workspace", type=Path, help="default: .workspace/<skill-name>")
    parser.add_argument("--iteration", type=int, help="default: next free iteration number")
    parser.add_argument("--baseline", choices=["without_skill", "old_skill"],
                        default="without_skill",
                        help="old_skill runs <workspace>/skill-snapshot/ as the baseline")
    parser.add_argument("--runs", type=int, default=1, help="repetitions per configuration")
    parser.add_argument("--only", nargs="+", metavar="EVAL", help="eval names or ids to run")
    parser.add_argument("--configs", nargs="+", metavar="CONFIG",
                        help="subset of configurations to run (e.g. with_skill)")
    parser.add_argument("--jobs", type=int, default=2, help="parallel runs")
    parser.add_argument("--timeout", type=int, default=900, help="seconds per run")
    parser.add_argument("--retries", type=int, default=2,
                        help="re-run a run whose agent ended in an error (rate limit, API failure)")
    parser.add_argument("--sandbox-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--dry-run", action="store_true", help="print the plan and exit")
    add_agent_args(parser)
    args = parser.parse_args()

    try:
        skill_dir = args.skill.resolve()
        name = skill_name(skill_dir)
        evals = load_evals(skill_dir)
        adapter = adapter_from_args(args)
    except HarnessError as exc:
        die(str(exc))

    workspace = (args.workspace or Path(".workspace") / name).resolve()
    if is_within(workspace, skill_dir):
        die("workspace must not be inside the skill directory")
    snapshot = workspace / "skill-snapshot"
    if args.baseline == "old_skill" and not (snapshot / "SKILL.md").is_file():
        die(f"--baseline old_skill needs a snapshot at {snapshot} (cp -r <skill> {snapshot})")
    configs = {"with_skill": skill_dir,
               args.baseline: snapshot if args.baseline == "old_skill" else None}
    if args.configs:
        unknown = set(args.configs) - set(configs)
        if unknown:
            die(f"unknown configurations: {', '.join(sorted(unknown))}")
        configs = {k: v for k, v in configs.items() if k in args.configs}

    if args.only:
        wanted = set(args.only)
        evals = [e for e in evals if str(e["id"]) in wanted or e.get("name") in wanted
                 or eval_dirname(e) in wanted]
        if not evals:
            die("--only matched no evals")

    iteration = args.iteration or next_iteration(workspace)
    iter_dir = workspace / f"iteration-{iteration}"
    jobs = []
    for ev in evals:
        eval_dir = iter_dir / eval_dirname(ev)
        for config, skill in configs.items():
            for k in range(1, args.runs + 1):
                jobs.append({"eval": ev, "eval_dir": eval_dir, "config": config, "skill": skill,
                             "run_dir": eval_dir / config / f"run-{k}",
                             "fixture": eval_dir / "fixture", "prompt": ev["prompt"]})

    if args.dry_run:
        for job in jobs:
            argv, stdin_text = adapter.command(job["prompt"], Path("<sandbox>/work"), args.model,
                                               ["<skill-args>"] if job["skill"] else [])
            print(f"{job['run_dir']}\n  skill: {job['skill'] or '-'}\n  argv: {argv}"
                  f"{'  (prompt on stdin)' if stdin_text is not None else ''}")
        print(f"{len(jobs)} runs planned in {iter_dir}")
        return 0

    try:
        for ev in evals:
            eval_dir = iter_dir / eval_dirname(ev)
            fixture = eval_dir / "fixture"
            if fixture.exists():
                shutil.rmtree(fixture)
            copy_fixture(skill_dir, ev.get("files", []), fixture)
            write_json(eval_dir / "eval_metadata.json", {
                "id": ev["id"], "name": ev.get("name") or str(ev["id"]), "prompt": ev["prompt"],
                "expected_output": ev["expected_output"],
                "assertions": normalize_assertions(ev.get("assertions"))})
    except HarnessError as exc:
        die(str(exc))
    write_json(iter_dir / "run_config.json", {
        "skill_name": name, "skill_dir": str(skill_dir),
        "snapshot_dir": str(snapshot) if args.baseline == "old_skill" else None,
        "agent": adapter.name, "model": args.model, "configurations": list(configs),
        "runs": args.runs, "created": utc_now()})

    failures = 0
    rows = []
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        futures = {pool.submit(run_one, job, adapter, args.model, args.timeout,
                               args.sandbox_root, args.retries): job for job in jobs}
        for future in as_completed(futures):
            job = futures[future]
            try:
                info = future.result()
            except HarnessError as exc:
                failures += 1
                print(f"error: {job['run_dir']}: {exc}", file=sys.stderr)
                continue
            if info["exit_code"] != 0 or info["error"]:
                failures += 1
            rows.append((eval_dirname(job["eval"]), job["config"], job["run_dir"].name, info))
            print(f"done {eval_dirname(job['eval'])}/{job['config']}/{job['run_dir'].name} "
                  f"exit={info['exit_code']} {info['seconds']:.1f}s", file=sys.stderr)

    print(f"{'eval':40} {'config':14} {'run':6} {'exit':>5} {'secs':>7} {'tokens':>8}  skill-read")
    for eval_name, config, run, info in sorted(rows, key=lambda r: r[:3]):
        exit_text = "T/O" if info["timed_out"] else "ERR" if info["error"] else str(info["exit_code"])
        tokens = "-" if info["tokens"] is None else str(info["tokens"])
        print(f"{eval_name:40} {config:14} {run:6} {exit_text:>5} {info['seconds']:7.1f} "
              f"{tokens:>8}  {','.join(info['read_skill']) or '-'}")
    print(f"iteration: {iter_dir}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
