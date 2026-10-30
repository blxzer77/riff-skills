#!/usr/bin/env python3
"""Pass if exactly one new ADR was added in docs/adr/ as 0003-*.md with a title."""

import re
import sys

sys.path.insert(0, __import__("os").path.dirname(__file__))
from adr_lib import fail, new_files, ok  # noqa: E402

files = new_files("docs/adr")
if len(files) != 1:
    fail(f"expected exactly 1 new ADR in docs/adr, found {[f.name for f in files]}")
f = files[0]
if not re.fullmatch(r"0003-[a-z0-9]+(-[a-z0-9]+)*\.md", f.name):
    fail(f"{f.name} does not follow the existing NNNN-kebab-title.md numbering (expected 0003-...)")
first = next((l for l in f.read_text().splitlines() if l.strip()), "")
if not first.startswith("#") and "title:" not in first:
    fail(f"{f.name} has no title heading")
ok(f"new ADR {f.name}")
