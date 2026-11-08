#!/usr/bin/env python3
"""Pass if no ADR-like file was created anywhere in the workdir."""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from adr_lib import FIXTURE, WORKDIR, fail, ok  # noqa: E402

created = []
for p in WORKDIR.rglob("*.md"):
    rel = p.relative_to(WORKDIR)
    if (FIXTURE / rel).exists():
        continue
    if re.search(r"(^|/)(adr|decisions?)(/|$)", str(rel.parent)) or re.match(r"\d{3,4}-", p.name):
        created.append(str(rel))
if created:
    fail(f"ADR created for a trivial change: {created}")
ok("no ADR created")
