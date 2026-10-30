#!/usr/bin/env python3
"""Assign a fixed train/validation split to trigger queries, stratified by should_trigger.

Only entries without a `set` are assigned; existing assignments are kept unless
--force is given, because moving queries between sets invalidates comparisons
across optimization iterations. The file is rewritten in place, order preserved.

Example:
    split_queries.py skills/writing-tests/evals/trigger-queries.json
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

from common import die, read_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("queries", type=Path, help="trigger-queries.json")
    parser.add_argument("--validation-fraction", type=float, default=0.4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--force", action="store_true", help="reassign every query")
    args = parser.parse_args()

    if not 0 < args.validation_fraction < 1:
        die("--validation-fraction must be between 0 and 1")
    queries = read_json(args.queries)
    if not isinstance(queries, list) or not all(
            isinstance(q, dict) and isinstance(q.get("query"), str)
            and isinstance(q.get("should_trigger"), bool) for q in queries):
        die("expected a list of {query: str, should_trigger: bool} objects")
    if args.force:
        for q in queries:
            q.pop("set", None)

    rng = random.Random(args.seed)
    assigned = 0
    for label in (True, False):
        group = [q for q in queries if q["should_trigger"] is label]
        todo = [q for q in group if "set" not in q]
        if not todo:
            continue
        existing_val = sum(1 for q in group if q.get("set") == "validation")
        target = round(len(group) * args.validation_fraction)
        if len(group) >= 2:
            target = min(max(target, 1), len(group) - 1)
        need = max(0, min(target - existing_val, len(todo)))
        rng.shuffle(todo)
        for i, q in enumerate(todo):
            q["set"] = "validation" if i < need else "train"
        assigned += len(todo)

    args.queries.write_text(json.dumps(queries, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
    counts = {(s, t): 0 for s in ("train", "validation") for t in (True, False)}
    for q in queries:
        counts[(q["set"], q["should_trigger"])] += 1
    print(json.dumps({"assigned": assigned,
                      "train": {"should_trigger": counts[("train", True)],
                                "should_not_trigger": counts[("train", False)]},
                      "validation": {"should_trigger": counts[("validation", True)],
                                     "should_not_trigger": counts[("validation", False)]}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
