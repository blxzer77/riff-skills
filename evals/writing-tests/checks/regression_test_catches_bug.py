#!/usr/bin/env python3
"""Shop eval: the agent's tests must pass on its fixed code and fail on the original code.

Copies the agent's tests/ directory onto the pristine fixture and runs the suite there.
If the new tests still pass against the buggy pricing.py, they do not guard the bug.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

WORKDIR = Path(os.environ["EVAL_WORKDIR"])
FIXTURE = Path(os.environ["EVAL_FIXTURE"])
CMD = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."]


def run(cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(CMD, cwd=cwd, capture_output=True, text=True, timeout=120)


after = run(WORKDIR)
if after.returncode != 0:
    print("FAIL: test suite does not pass on the agent's final code")
    print(after.stderr[-1500:])
    sys.exit(1)

with tempfile.TemporaryDirectory() as tmp:
    before_dir = Path(tmp) / "before"
    shutil.copytree(FIXTURE, before_dir)
    shutil.rmtree(before_dir / "tests")
    shutil.copytree(WORKDIR / "tests", before_dir / "tests")
    before = run(before_dir)

if before.returncode == 0:
    print("FAIL: the agent's tests also pass on the original buggy code; no test reproduces the bug")
    sys.exit(1)
print("PASS: suite passes after the fix and fails on the original code")
print(before.stderr[-800:])
