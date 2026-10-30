#!/usr/bin/env python3
"""Sessions eval: the suite passes 20 runs in a row, still covers expiry, and does not sleep."""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

WORKDIR = Path(os.environ["EVAL_WORKDIR"])
RUNS = 20


def run(cwd: Path) -> int:
    return subprocess.run(["node", "--test"], cwd=cwd, capture_output=True, text=True, timeout=120).returncode


failures = sum(run(WORKDIR) != 0 for _ in range(RUNS))
if failures:
    print(f"FAIL: suite failed {failures}/{RUNS} runs; still nondeterministic")
    sys.exit(1)

tests = "\n".join(p.read_text() for p in (WORKDIR / "test").rglob("*.js"))
if re.search(r"setTimeout|sleep\(", tests) and not re.search(r"mock\.timers|useFakeTimers|now\s*[:=]|clock", tests):
    print("FAIL: tests still wait on real time")
    sys.exit(1)

# Expiry must still be tested: a store that never expires sessions has to fail the suite.
with tempfile.TemporaryDirectory() as tmp:
    d = Path(tmp) / "w"
    shutil.copytree(WORKDIR, d, ignore=shutil.ignore_patterns("node_modules", ".git"))
    src = (d / "src/session.js").read_text()
    never_expires = re.sub(r"if \((.*?)>\s*this\.ttlMs\)", r"if (false)", src, count=1)
    if never_expires == src:
        never_expires = src.replace("this.ttlMs", "Infinity")
    (d / "src/session.js").write_text(never_expires)
    if run(d) == 0:
        print("FAIL: suite passes even when sessions never expire; expiry is no longer tested")
        sys.exit(1)

print(f"PASS: {RUNS}/{RUNS} green runs, no real-time waits, expiry still verified")
