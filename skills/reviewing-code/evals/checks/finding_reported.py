#!/usr/bin/env python3
"""Pass when the response reports a finding inside a given file and line range.

Arguments (the assertion's `args` in evals.json) are `<path> <start> <end>`.
"""

import sys

from review_lib import hits, parse, response_text

args = sys.argv[1:]
path, start, end = args[0], int(args[1]), int(args[2])
findings, _ = parse(response_text())
if hits(findings, path, range(start, end + 1)):
    print(f"PASS: finding reported at {path}:{start}-{end}")
    sys.exit(0)
print(f"FAIL: no finding at {path}:{start}-{end}; findings were {findings}")
sys.exit(1)
