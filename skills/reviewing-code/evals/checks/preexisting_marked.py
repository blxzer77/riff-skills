#!/usr/bin/env python3
"""Pass when a defect at a location is listed as pre-existing and not as a finding.

Arguments are `<path> <start> <end>`.
"""

import sys

from review_lib import hits, parse, response_text

args = sys.argv[1:]
path, start, end = args[0], int(args[1]), int(args[2])
findings, preexisting = parse(response_text())
lines = range(start, end + 1)
if hits(findings, path, lines):
    print(f"FAIL: pre-existing defect reported as a finding at {path}:{start}-{end}")
    sys.exit(1)
if not hits(preexisting, path, lines):
    print(f"FAIL: pre-existing defect at {path}:{start}-{end} not listed; pre-existing entries {preexisting}")
    sys.exit(1)
print(f"PASS: {path}:{start}-{end} listed as pre-existing only")
