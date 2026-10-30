#!/usr/bin/env python3
"""Pass if `python -m csvtool --delimiter ';' file` reads semicolon-separated data."""

import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
from adr_lib import WORKDIR, fail, ok  # noqa: E402

with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
    f.write("a;b\n1;2\n3;4\n")
    path = f.name
try:
    out = subprocess.run(
        [sys.executable, "-m", "csvtool", "--delimiter", ";", path],
        cwd=WORKDIR, capture_output=True, text=True, timeout=30,
    )
finally:
    os.unlink(path)
if out.returncode != 0:
    fail(f"command failed: {out.stderr.strip()[-500:]}")
if "2 rows" not in out.stdout or "a, b" not in out.stdout:
    fail(f"unexpected output: {out.stdout.strip()[:300]}")
ok("--delimiter works")
