#!/usr/bin/env python3
"""api-server eval: a shared session store was adopted, and an ADR recording it was added
in docs/adr/ with the project's numbering, real options, and a cost."""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from adr_lib import WORKDIR, fail, find_section, new_files, ok, sections  # noqa: E402

src = "\n".join(p.read_text() for p in (WORKDIR / "src").rglob("*.*js"))
if not re.search(r"\bstore\s*[:,}]|connect-pg-simple|connect-redis|new \w*Store\(", src):
    fail("express-session still uses the default in-memory store")

files = [p for p in new_files("docs/adr") if p.name.lower() != "readme.md"]
if len(files) != 1:
    fail(f"expected one new ADR in docs/adr, found {[p.name for p in files]}")
adr = files[0]
if not re.fullmatch(r"0002-[a-z0-9]+(-[a-z0-9]+)*\.md", adr.name):
    fail(f"{adr.name} does not continue the numbering (expected 0002-...)")
text = adr.read_text()
secs = sections(text)
opts = find_section(secs, "option", "alternative")
listed = len(re.findall(r"^\s*(?:[-*]|\d+[.)])\s+\S", opts or "", flags=re.M))
if listed < 2 and len(re.findall(r"\b(redis|postgres|pg|connect-pg-simple|sticky|jwt|memcached)\b",
                                  text, re.I)) < 2:
    fail("ADR does not compare at least two real options")
cons = find_section(secs, "consequence") or ""
if not re.search(r"\b(bad|cost|downside|drawback|risk|harder|slower|latency|load|accept)", cons, re.I):
    fail("ADR states no cost of the decision")
ok(f"store configured and {adr.name} records the decision")
