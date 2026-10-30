#!/usr/bin/env python3
"""Pass if a new portable skill exists under skills/ and captures the notes' gotchas."""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from skill_lib import WORKDIR, check_portable, fail, load_skill, ok  # noqa: E402

skills = [p.parent for p in WORKDIR.glob("skills/*/SKILL.md")]
if len(skills) != 1:
    fail(f"expected one skill under skills/, found {[str(s) for s in skills]}")
skill = skills[0]
check_portable(skill)
_, body = load_skill(skill)
everything = body + "".join(p.read_text() for p in skill.rglob("*.md") if p.name != "SKILL.md")
required = {
    "both version files": r"package\.json",
    "tag must start with v": r"\bv\d|vX\.Y\.Z|v<",
    "npm publish after release assets exist": r"npm publish",
}
missing = [k for k, pat in required.items() if not re.search(pat, everything)]
if missing:
    fail(f"skill omits gotchas from the notes: {missing}")
ok(f"{skill.name} is portable and keeps the release gotchas")
