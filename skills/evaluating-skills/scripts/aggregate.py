#!/usr/bin/env python3
"""Aggregate graded runs of one iteration into benchmark.json and benchmark.md.

Per eval, each configuration's pass rate, time and tokens are averaged over its
runs; run_summary then takes the mean and population stddev across evals.
delta is always primary (with_skill) minus baseline (without_skill / old_skill).

Example:
    aggregate.py --iteration .workspace/writing-tests/iteration-1
"""

from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

from common import die, read_json, utc_now, write_json

PRIMARY = "with_skill"
BASELINES = ("without_skill", "old_skill")


def mean(values):
    values = [v for v in values if v is not None]
    return statistics.fmean(values) if values else None


def spread(values, digits=4):
    values = [v for v in values if v is not None]
    if not values:
        return {"mean": None, "stddev": None}
    sd = statistics.pstdev(values) if len(values) > 1 else 0.0
    if digits == 0:
        return {"mean": round(statistics.fmean(values)), "stddev": round(sd)}
    return {"mean": round(statistics.fmean(values), digits), "stddev": round(sd, digits)}


def collect(config_dir: Path) -> dict:
    rates, times, tokens, verdicts, assertion_texts = [], [], [], {}, {}
    counts = {"requested_runs": 0, "completed_runs": 0, "errored_runs": 0,
              "timed_out_runs": 0, "untreated_runs": 0, "missing_grading_runs": 0,
              "invalid_grading_runs": 0, "missing_token_runs": 0, "retry_runs": 0,
              "retry_attempts": 0, "retry_error_attempts": 0}
    runs = sorted(config_dir.glob("run-*"))
    counts["requested_runs"] = len(runs)
    for run in runs:
        timing = read_json(run / "timing.json") if (run / "timing.json").is_file() else {}
        if timing.get("timed_out"):
            counts["timed_out_runs"] += 1
            print(f"warning: {run} timed out; excluded", file=sys.stderr)
            continue
        if timing.get("error"):
            counts["errored_runs"] += 1
            print(f"warning: {run} ended in an agent error; excluded", file=sys.stderr)
            continue
        if timing.get("treatment_status") == "not_treated":
            counts["untreated_runs"] += 1
            print(f"warning: {run} did not load the skill; excluded", file=sys.stderr)
            continue
        grading = read_json(run / "grading.json") if (run / "grading.json").is_file() else None
        if grading is None:
            counts["missing_grading_runs"] += 1
            print(f"warning: {run} has no grading.json; excluded", file=sys.stderr)
            continue
        if grading.get("status", "valid") != "valid":
            counts["invalid_grading_runs"] += 1
            print(f"warning: {run} has invalid grading; excluded", file=sys.stderr)
            continue
        summary = grading.get("summary", {})
        rates.append(summary.get("pass_rate"))
        counts["completed_runs"] += 1
        retry_count = timing.get("retry_count", 0)
        counts["retry_runs"] += int(retry_count > 0)
        counts["retry_attempts"] += retry_count
        counts["retry_error_attempts"] += timing.get("retry_error_count", 0)
        if timing.get("duration_ms") is not None:
            times.append(timing["duration_ms"] / 1000)
        token_count = timing.get("total_tokens")
        tokens.append(token_count)
        if token_count is None:
            counts["missing_token_runs"] += 1
        for result in grading.get("assertion_results", []):
            key = result.get("id") or result.get("text")
            verdicts.setdefault(key, []).append(bool(result.get("passed")))
            assertion_texts[key] = result.get("text", key)
    avg_tokens = mean(tokens)
    return {"pass_rate": None if mean(rates) is None else round(mean(rates), 4),
            "time_seconds": None if mean(times) is None else round(mean(times), 2),
            "tokens": None if avg_tokens is None else round(avg_tokens),
            "runs": len(rates), "counts": counts,
            "_majority": {t: sum(v) * 2 > len(v) for t, v in verdicts.items()},
            "_assertions": {
                t: {"text": assertion_texts[t], "passed": sum(v), "total": len(v),
                    "rate": round(sum(v) / len(v), 4)}
                for t, v in verdicts.items()
            }}


def delta(a, b):
    return None if a is None or b is None else round(a - b, 4)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--iteration", required=True, type=Path, help="iteration-N directory")
    args = parser.parse_args()
    iter_dir = args.iteration.resolve()
    if not iter_dir.is_dir():
        die(f"no such iteration directory: {iter_dir}")
    config = read_json(iter_dir / "run_config.json") if (iter_dir / "run_config.json").is_file() \
        else {}

    per_eval = {}
    for eval_dir in sorted(iter_dir.glob("eval-*")):
        configs = {}
        for config_dir in sorted(p for p in eval_dir.iterdir() if p.is_dir() and p.name != "fixture"):
            data = collect(config_dir)
            if data:
                configs[config_dir.name] = data
        if configs:
            per_eval[eval_dir.name.removeprefix("eval-")] = configs
    if not per_eval:
        die(f"no graded runs under {iter_dir}; run grade.py first")

    names = sorted({c for configs in per_eval.values() for c in configs})
    primary = PRIMARY if PRIMARY in names else next((n for n in names if n not in BASELINES), names[0])
    baseline = next((n for n in BASELINES if n in names and n != primary),
                    next((n for n in names if n != primary), None))

    summary = {}
    for name in names:
        rows = [configs[name] for configs in per_eval.values() if name in configs]
        summary[name] = {"pass_rate": spread([r["pass_rate"] for r in rows]),
                         "time_seconds": spread([r["time_seconds"] for r in rows], 2),
                         "tokens": spread([r["tokens"] for r in rows], 0),
                         "counts": {
                             key: sum(r.get("counts", {}).get(key, 0) for r in rows)
                             for key in ("requested_runs", "completed_runs", "errored_runs",
                                         "timed_out_runs", "untreated_runs",
                                         "missing_grading_runs", "invalid_grading_runs",
                                         "missing_token_runs", "retry_runs", "retry_attempts",
                                         "retry_error_attempts")
                         }}
    if baseline:
        paired = [(configs[primary], configs[baseline]) for configs in per_eval.values()
                  if primary in configs and baseline in configs and
                  configs[primary]["pass_rate"] is not None and
                  configs[baseline]["pass_rate"] is not None]
        summary["delta"] = {
            m: (round(statistics.fmean(values), 4) if values else None)
            for m, values in {
                "pass_rate": [a["pass_rate"] - b["pass_rate"] for a, b in paired],
                "time_seconds": [a["time_seconds"] - b["time_seconds"] for a, b in paired
                                 if a["time_seconds"] is not None and b["time_seconds"] is not None],
                "tokens": [a["tokens"] - b["tokens"] for a, b in paired
                           if a["tokens"] is not None and b["tokens"] is not None],
            }.items()
        }
        if summary["delta"]["tokens"] is not None:
            summary["delta"]["tokens"] = round(summary["delta"]["tokens"])
        summary["delta_evals"] = len(paired)

    patterns = {"pass_both": [], "fail_both": [], "primary_only": [], "baseline_only": []}
    if baseline:
        for eval_name, configs in per_eval.items():
            if primary not in configs or baseline not in configs:
                continue
            p, b = configs[primary]["_majority"], configs[baseline]["_majority"]
            for assertion_id in p.keys() & b.keys():
                key = {(True, True): "pass_both", (False, False): "fail_both",
                       (True, False): "primary_only", (False, True): "baseline_only"}[
                           (p[assertion_id], b[assertion_id])]
                text = configs[primary].get("_assertions", {}).get(assertion_id, {}).get(
                    "text", assertion_id)
                patterns[key].append(f"{eval_name}: {text}")
        for value in patterns.values():
            value.sort()

    iteration = iter_dir.name.removeprefix("iteration-")
    benchmark = {
        "metadata": {"skill_name": config.get("skill_name"),
                     "iteration": int(iteration) if iteration.isdigit() else iteration,
                     "agent": config.get("agent"), "model": config.get("model"),
                     "primary": primary, "baseline": baseline, "timestamp": utc_now()},
        "evals": [{"name": eval_name,
                   **{c: {k: v for k, v in d.items()
                          if k not in ("_majority", "_assertions")}
                       | {"assertions": d.get("_assertions", {})}
                      for c, d in configs.items()}}
                  for eval_name, configs in per_eval.items()],
        "run_summary": summary,
        "assertion_patterns": patterns,
    }
    write_json(iter_dir / "benchmark.json", benchmark)
    (iter_dir / "benchmark.md").write_text(render(benchmark, names), encoding="utf-8")
    print(render(benchmark, names))
    return 0


def fmt(value, digits=2):
    if value is None:
        return "-"
    return f"{value:.{digits}f}" if isinstance(value, float) else str(value)


def render(bench: dict, names: list[str]) -> str:
    meta = bench["metadata"]
    lines = [f"# Benchmark: {meta['skill_name']} iteration {meta['iteration']}", "",
             f"Agent `{meta['agent']}`, model `{meta['model'] or 'default'}`; "
             f"primary `{meta['primary']}`, baseline `{meta['baseline'] or '-'}`.", "",
             "| eval | " + " | ".join(f"{n} pass / s / tokens" for n in names) + " |",
             "|---|" + "---|" * len(names)]
    for row in bench["evals"]:
        cells = []
        for n in names:
            d = row.get(n)
            cells.append("-" if d is None else
                         f"{fmt(d['pass_rate'])} / {fmt(d['time_seconds'], 1)} / {fmt(d['tokens'])}")
        lines.append(f"| {row['name']} | " + " | ".join(cells) + " |")
    lines += ["", "| metric | " + " | ".join(names) + (" | delta |" if "delta" in bench["run_summary"] else " |"),
              "|---|" + "---|" * (len(names) + ("delta" in bench["run_summary"]))]
    for metric in ("pass_rate", "time_seconds", "tokens"):
        cells = [f"{fmt(bench['run_summary'][n][metric]['mean'])} ± "
                 f"{fmt(bench['run_summary'][n][metric]['stddev'])}" for n in names]
        if "delta" in bench["run_summary"]:
            cells.append(fmt(bench["run_summary"]["delta"][metric]))
        lines.append(f"| {metric} | " + " | ".join(cells) + " |")
    lines.append("")
    for key, label in (("primary_only", "Pass only with the skill (value added)"),
                       ("baseline_only", "Pass only in the baseline (regressions)"),
                       ("fail_both", "Fail in both (broken assertion or too hard)"),
                       ("pass_both", "Pass in both (non-discriminating; replace)")):
        items = bench["assertion_patterns"][key]
        if items:
            lines += [f"**{label}**", ""] + [f"- {i}" for i in items] + [""]
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
