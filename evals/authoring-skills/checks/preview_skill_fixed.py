#!/usr/bin/env python3
"""Pass if the deploying-previews skill was made portable and its padding removed."""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from skill_lib import WORKDIR, check_portable, fail, load_skill, ok  # noqa: E402

skill = WORKDIR / "skills" / "deploying-previews"
if not (skill / "SKILL.md").is_file():
    fail("skills/deploying-previews/SKILL.md missing")
check_portable(skill)
_, body = load_skill(skill)
if re.search(r"Environment variables are key-value pairs|A preview deployment is a temporary", body):
    fail("background the agent already knows is still in the body")
if re.search(r"\b[A-Z]{4,}\b.*!{2,}", body):
    fail("shouted rules without reasons remain")
if re.search(r"Pick whichever", body):
    fail("still presents a menu of platforms with no default")
ok("deploying-previews is portable and trimmed")
