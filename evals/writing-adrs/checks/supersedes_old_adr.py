#!/usr/bin/env python3
"""Pass if 0001 is marked superseded (decision text intact) and a new 0002 ADR links back."""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from adr_lib import FIXTURE, WORKDIR, fail, new_files, ok  # noqa: E402

old_path = "docs/decisions/0001-poll-for-notifications.md"
old = (WORKDIR / old_path).read_text() if (WORKDIR / old_path).exists() else None
if old is None:
    fail("0001 was deleted or renamed")
if not re.search(r"supersed", old, re.I):
    fail("0001 is not marked as superseded")
orig_decision = "We will poll `GET /api/notifications?since=<ts>` every 5 seconds from the browser."
if orig_decision not in old:
    fail("0001's original decision text was rewritten; it should be kept and superseded")

new = new_files("docs/decisions")
new = [p for p in new if p.name != "README.md"]
if len(new) != 1 or not new[0].name.startswith("0002-"):
    fail(f"expected one new ADR 0002-*.md in docs/decisions, found {[p.name for p in new]}")
if not re.search(r"0001|poll-for-notifications", new[0].read_text()):
    fail(f"{new[0].name} does not reference the ADR it supersedes")
index = (WORKDIR / "docs/decisions/README.md").read_text()
if "0002" not in index:
    fail("index README.md not updated with 0002")
_ = FIXTURE
ok(f"0001 superseded, {new[0].name} added and indexed")
