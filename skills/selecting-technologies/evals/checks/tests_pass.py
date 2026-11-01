#!/usr/bin/env python3
"""Pass when the project's unittest suite passes after a clean install of
requirements.txt, with no network access needed by the tests themselves."""

from tech_lib import WORKDIR, fail, install_and_run, ok

passed, out = install_and_run(WORKDIR / "requirements.txt", ["-m", "unittest", "-q"])
if not passed:
    fail("tests fail after a clean install of requirements.txt: " + out[-800:])
summary = [l for l in out.strip().splitlines() if l.startswith("Ran ")]
ok("tests pass after a clean install" + (f" ({summary[-1]})" if summary else ""))
