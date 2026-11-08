#!/usr/bin/env python3
"""Pass when the review names the project fact that decides the case.

Arguments (the assertion's `args`) are regular expressions; every one must match
the final response, case-insensitively. Each pattern lists several wordings of one
fact, so the check does not depend on phrasing the prompt never asked for.
"""

import sys

from design_lib import missing, response_text

patterns = sys.argv[1:]
if not patterns:
    print("FAIL: no patterns given")
    sys.exit(1)
text = response_text()
absent = missing(text, patterns)
if not text.strip():
    print("FAIL: empty response")
    sys.exit(1)
if absent:
    print(f"FAIL: the review does not name the deciding fact; unmatched: {absent}")
    sys.exit(1)
print("PASS: the review names the deciding fact")
