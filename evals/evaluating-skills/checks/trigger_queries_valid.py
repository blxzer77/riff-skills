#!/usr/bin/env python3
"""Validate trigger queries for the skill present in the fixture."""
import json, os, sys
from pathlib import Path

def main():
    root = Path(os.environ["EVAL_WORKDIR"])
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if target is None:
        candidates = list(root.glob("**/evals/trigger-queries.json"))
        target = candidates[0] if candidates else None
    if target is None or not target.is_file():
        print("FAIL: no trigger-queries.json found in artifact", file=sys.stderr); return 1
    try: qs = json.loads(target.read_text())
    except json.JSONDecodeError as exc:
        print(f"FAIL: invalid JSON: {exc}", file=sys.stderr); return 1
    if not isinstance(qs, list) or not all(isinstance(q, dict) and isinstance(q.get("query"), str) and isinstance(q.get("should_trigger"), bool) for q in qs):
        print("FAIL: expected list of query/should_trigger records", file=sys.stderr); return 1
    pos = sum(q["should_trigger"] for q in qs); neg = len(qs)-pos
    if not 16 <= len(qs) <= 24 or pos < 7 or neg < 7:
        print(f"FAIL: {len(qs)} queries ({pos} positive, {neg} negative)", file=sys.stderr); return 1
    if len({q["query"].strip().lower() for q in qs}) != len(qs):
        print("FAIL: duplicate queries", file=sys.stderr); return 1
    print(f"PASS: {target} ({len(qs)} queries, {pos} positive / {neg} negative)"); return 0
if __name__ == "__main__": sys.exit(main())
