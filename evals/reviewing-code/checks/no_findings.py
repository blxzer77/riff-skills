#!/usr/bin/env python3
"""Pass when the response reports zero findings at a `path:line` location.

The wording of the no-findings verdict is a format choice, not review quality, so it
is checked separately by an LLM-graded assertion rather than by exact text here.
"""

import sys

from review_lib import parse, response_text

findings, _ = parse(response_text())
if findings:
    print(f"FAIL: expected no findings, got {findings}")
    sys.exit(1)
print("PASS: no findings reported")
