#!/usr/bin/env python3
"""Check that a benchmark interpretation uses artifact-derived categories."""
import json, os, sys
from pathlib import Path

def main():
    data = json.loads(next(Path(os.environ["EVAL_WORKDIR"]).glob("**/benchmark.json")).read_text())
    ids = {r.get("id") for r in data.get("records", [])}
    required = {"both-pass","both-fail","primary-only","baseline-only","untreated","timeout","error","invalid"}
    if not required <= ids: print(f"FAIL: missing records {required-ids}"); return 1
    text = Path(os.environ["EVAL_RESPONSE"]).read_text().lower()
    categories = {
        "pass-both": ("both-pass", "pass both", "both pass"),
        "fail-both": ("both-fail", "fail both", "both fail"),
        "primary-only": ("primary-only", "with-skill only", "only with"),
        "baseline-only": ("baseline-only", "without-skill only", "only baseline"),
        "untreated": ("untreated", "not_treated", "not treated"),
        "timeout": ("timeout", "timed out", "time-out"),
        "error": ("api error", "infrastructure error", "error"),
        "invalid": ("invalid grading", "invalid grader", "invalid"),
    }
    missing = [label for label, choices in categories.items() if not any(x in text for x in choices)]
    if missing: print("FAIL: missing benchmark categories " + ", ".join(missing)); return 1
    if not any(x in text for x in ("not enough", "cannot", "can't", "insufficient")): print("FAIL: no limitation conclusion"); return 1
    if not any(x in text for x in ("token", "cost")): print("FAIL: no cost discussion"); return 1
    print("PASS: interpretation addresses all artifact categories, limitations, and cost"); return 0
if __name__ == "__main__": sys.exit(main())
