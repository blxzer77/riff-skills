#!/usr/bin/env python3
"""Pass if the new ADR names >= 2 options and states at least one negative consequence.

Options may live in their own section or inside the decision text (projects whose
ADRs use only Context / Decision / Consequences put alternatives there); both count.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from adr_lib import fail, find_section, new_files, ok, sections  # noqa: E402

ADR_DIR = os.environ.get("ADR_DIR", "docs/adr")

files = [p for p in new_files(ADR_DIR) if p.name.lower() != "readme.md"]
if not files:
    fail(f"no new ADR in {ADR_DIR}")
text = files[-1].read_text()
secs = sections(text)

ITEM = r"^\s*(?:[-*]|\d+[.)])\s+\S"
options = find_section(secs, "option", "alternative")
count = len(re.findall(ITEM, options, flags=re.M)) if options else 0
# MADR style: options as sub-headings under an "Options" heading.
block = re.search(r"^(#{2,3})\s+[^\n]*(?:option|alternative)[^\n]*\n(.*?)(?=^\1\s|\Z)", text, re.I | re.M | re.S)
if block:
    count = max(count, len(re.findall(r"^#{3,6}\s+\S", block.group(2), flags=re.M)))
# Alternatives argued inside the decision section ("X rather than the alternatives: - **Y** — ...").
decision = find_section(secs, "decision") or ""
if re.search(r"\b(alternative|rather than|instead of|considered|rejected|over )", decision, re.I):
    count = max(count, 1 + len(re.findall(r"^\s*[-*]\s+\*\*[^*]+\*\*", decision, flags=re.M)))
if count < 2:
    fail("fewer than two options considered")

cons = find_section(secs, "consequence")
if cons is None:
    fail("no consequences section")
negative = re.search(r"\b(bad|cost|downside|drawback|risk|negative|trade-?off|harder|slower|more complex|accept)", cons, re.I)
if not negative:
    fail("consequences state no cost or downside")
ok(f"{files[-1].name}: {count} options and a negative consequence present")
