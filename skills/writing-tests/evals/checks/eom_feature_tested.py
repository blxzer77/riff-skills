#!/usr/bin/env python3
"""Invoices eval: 'eom' terms implemented, and the agent added tests that pin it down.

Checks (1) a hidden oracle for end-of-month terms, (2) the suite passes, and
(3) the agent's tests fail against two plausible wrong implementations.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

WORKDIR = Path(os.environ["EVAL_WORKDIR"])
CMD = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."]

ORACLE = r"""
from datetime import date
from invoices.due import due_date
assert due_date(date(2026, 1, 15), "eom") == date(2026, 1, 31)
assert due_date(date(2026, 2, 3), "eom") == date(2026, 2, 28)
assert due_date(date(2028, 2, 3), "eom") == date(2028, 2, 29)
assert due_date(date(2026, 4, 30), "eom") == date(2026, 4, 30)
assert due_date(date(2026, 12, 9), "eom") == date(2026, 12, 31)
assert due_date(date(2026, 3, 2), "net30") == date(2026, 4, 1)
"""

MUTANTS = {
    "always-31st": (
        "from datetime import date, timedelta\n"
        "TERMS_DAYS = {'net15': 15, 'net30': 30, 'net60': 60}\n"
        "def due_date(issued, terms):\n"
        "    if terms == 'eom':\n"
        "        try:\n            return issued.replace(day=31)\n"
        "        except ValueError:\n            return issued.replace(day=30)\n"
        "    return issued + timedelta(days=TERMS_DAYS[terms])\n"
    ),
    "ignores-leap-year": (
        "from datetime import date, timedelta\n"
        "TERMS_DAYS = {'net15': 15, 'net30': 30, 'net60': 60}\n"
        "DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]\n"
        "def due_date(issued, terms):\n"
        "    if terms == 'eom':\n"
        "        return issued.replace(day=DAYS[issued.month - 1])\n"
        "    return issued + timedelta(days=TERMS_DAYS[terms])\n"
    ),
    "plus-30-days": (
        "from datetime import date, timedelta\n"
        "TERMS_DAYS = {'net15': 15, 'net30': 30, 'net60': 60, 'eom': 30}\n"
        "def due_date(issued, terms):\n"
        "    return issued + timedelta(days=TERMS_DAYS[terms])\n"
    ),
}


def run(cwd, args):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=120)


oracle = run(WORKDIR, [sys.executable, "-c", ORACLE])
if oracle.returncode != 0:
    print("FAIL: eom terms not implemented correctly")
    print(oracle.stderr[-800:])
    sys.exit(1)
suite = run(WORKDIR, CMD)
if suite.returncode != 0:
    print("FAIL: test suite does not pass")
    print(suite.stderr[-800:])
    sys.exit(1)

survivors = []
with tempfile.TemporaryDirectory() as tmp:
    for name, src in MUTANTS.items():
        d = Path(tmp) / name
        shutil.copytree(WORKDIR, d, ignore=shutil.ignore_patterns("__pycache__", ".git"))
        (d / "invoices/due.py").write_text(src)
        if run(d, CMD).returncode == 0:
            survivors.append(name)
if survivors:
    print(f"FAIL: tests do not catch wrong eom implementations: {', '.join(survivors)}")
    sys.exit(1)
print(f"PASS: eom implemented; tests catch all {len(MUTANTS)} wrong implementations")
