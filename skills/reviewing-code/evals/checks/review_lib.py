"""Shared parsing for reviewing-code eval checks.

A finding is a line that starts with `[path:line]` or `[path:start-end]`. Lines that
appear after a "Pre-existing" heading are pre-existing entries, not findings.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

# Accepts `[path:12]`, `[path:12-18]`, and the same wrapped in backticks or bold,
# optionally after a list marker or number, at the start of a line.
LOCATION = re.compile(
    r"^\s*(?:[-*]|\d+[.)])?\s*(?:\*\*|`)?\s*\[?`?([\w./-]+\.\w+):(\d+)(?:[-–](\d+))?`?\]?"
)
# A location inside the patch file itself points at the diff, not at reviewed code.
IGNORED_SUFFIXES = (".patch", ".diff")


def response_text() -> str:
    return Path(os.environ["EVAL_RESPONSE"]).read_text(encoding="utf-8", errors="replace")


def parse(text: str) -> tuple[list[tuple[str, int, int]], list[tuple[str, int, int]]]:
    findings, preexisting = [], []
    target = findings
    for line in text.splitlines():
        if re.match(r"^\s*#*\s*\**\s*pre-?existing", line, re.IGNORECASE):
            target = preexisting
            continue
        if re.match(r"^\s*#*\s*\**\s*checked\b", line, re.IGNORECASE):
            target = findings
            continue
        match = LOCATION.match(line)
        if match and not match.group(1).endswith(IGNORED_SUFFIXES):
            start = int(match.group(2))
            end = int(match.group(3) or start)
            target.append((Path(match.group(1)).as_posix().lstrip("./"), start, end))
    return findings, preexisting


def hits(entries, path: str, lines: range) -> bool:
    path = path.lstrip("./")
    return any(p.endswith(path) and s <= lines.stop - 1 and e >= lines.start
               for p, s, e in entries)
