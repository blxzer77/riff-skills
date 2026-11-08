#!/usr/bin/env python3
"""Decline eval: a generic topic request must not create a new skill."""

import os
import sys
from pathlib import Path

workdir = Path(os.environ["EVAL_WORKDIR"])
created = []
for path in workdir.rglob("SKILL.md"):
    relative = path.relative_to(workdir)
    if relative.parts[:3] == (".claude", "skills", "authoring-skills"):
        continue
    created.append(relative.as_posix())

if created:
    print("FAIL: generic skill artifacts were created:")
    print("\n".join(created))
    sys.exit(1)
print("PASS: no new skill artifact was created")
