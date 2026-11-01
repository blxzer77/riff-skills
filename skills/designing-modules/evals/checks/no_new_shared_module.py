#!/usr/bin/env python3
"""Pass when the change adds no shared grab-bag module (utils, common, shared, core,
helpers, ...) under shop/ that did not exist in the fixture."""

import os
import sys
from pathlib import Path

from module_lib import GRAB_BAG_NAMES, grab_bag_modules

fixture = Path(os.environ["EVAL_FIXTURE"]) / "shop"
before = {p.stem for p in fixture.iterdir()} if fixture.is_dir() else set()
added = [m for m in grab_bag_modules() if m.split(".")[1] not in before]
if added:
    print(f"FAIL: new shared module(s) added: {added}; names checked: {sorted(GRAB_BAG_NAMES)}")
    sys.exit(1)
print("PASS: no new shared grab-bag module")
