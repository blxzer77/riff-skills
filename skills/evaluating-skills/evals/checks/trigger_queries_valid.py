#!/usr/bin/env python3
"""Pass if skills/writing-adrs/evals/trigger-queries.json is a valid, balanced query set."""

import json
import os
import sys
from pathlib import Path

path = Path(os.environ["EVAL_WORKDIR"]) / "skills/writing-adrs/evals/trigger-queries.json"
if not path.is_file():
    print(f"FAIL: {path.name} not found at skills/writing-adrs/evals/")
    sys.exit(1)
try:
    qs = json.loads(path.read_text())
except json.JSONDecodeError as exc:
    print(f"FAIL: invalid JSON: {exc}")
    sys.exit(1)
if not isinstance(qs, list) or not all(isinstance(q, dict) and isinstance(q.get("query"), str)
                                       and isinstance(q.get("should_trigger"), bool) for q in qs):
    print("FAIL: expected a list of {query: str, should_trigger: bool}")
    sys.exit(1)
pos = sum(q["should_trigger"] for q in qs)
neg = len(qs) - pos
if not 16 <= len(qs) <= 24 or pos < 7 or neg < 7:
    print(f"FAIL: {len(qs)} queries ({pos} positive, {neg} negative); want 16-24 with >= 7 of each")
    sys.exit(1)
if len({q["query"].strip().lower() for q in qs}) != len(qs):
    print("FAIL: duplicate queries")
    sys.exit(1)
print(f"PASS: {len(qs)} queries, {pos} positive / {neg} negative")
