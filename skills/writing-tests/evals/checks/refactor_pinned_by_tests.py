#!/usr/bin/env python3
"""Report eval: behavior preserved, and the agent added tests that pin current behavior.

(1) The refactored formatReport matches the original on a set of hidden inputs.
(2) The agent added at least one test file and the suite passes.
(3) The agent's tests fail against plausible behavior changes a refactor could introduce.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

WORKDIR = Path(os.environ["EVAL_WORKDIR"])
FIXTURE = Path(os.environ["EVAL_FIXTURE"])

CASES = [
    [{"name": "Ana", "quota": 10}, [{"kind": "api_call", "units": 7}, {"kind": "upload", "units": 5},
                                    {"kind": "login", "units": 3}]],
    [{"quota": 10}, []],
    [{"name": "", "quota": 100}, [{"kind": "export", "units": 1}, {"kind": "export", "units": 2}]],
    [{"name": "Bo", "quota": 3}, [{"kind": "login", "units": 9}]],
    [{"name": "Cy", "quota": 6}, [{"kind": "upload", "units": 3}, {"kind": "api_call", "units": 3}]],
    [{"name": "Di", "quota": 1}, [{"kind": "api_call", "units": 1}, {"kind": "api_call", "units": 1},
                                  {"kind": "upload", "units": 1}]],
]

PROBE = """
import { formatReport } from "./src/report.js";
const cases = JSON.parse(process.argv[2]);
console.log(JSON.stringify(cases.map(([u, e]) => formatReport(u, e))));
"""


def outputs(root: Path):
    probe = root / "probe.mjs"
    probe.write_text(PROBE)
    try:
        r = subprocess.run(["node", "probe.mjs", json.dumps(CASES)], cwd=root,
                           capture_output=True, text=True, timeout=60)
    finally:
        probe.unlink()
    if r.returncode != 0:
        return None, r.stderr[-800:]
    return json.loads(r.stdout), ""


expected, err = outputs(FIXTURE)
actual, err2 = outputs(WORKDIR)
if actual is None:
    print(f"FAIL: refactored formatReport crashed: {err2}")
    sys.exit(1)
if actual != expected:
    diffs = [i for i, (a, b) in enumerate(zip(actual, expected)) if a != b]
    print(f"FAIL: behavior changed by the refactor on cases {diffs}")
    sys.exit(1)

tests = [p for p in WORKDIR.rglob("*.test.*js") if "node_modules" not in p.parts] + \
        [p for p in WORKDIR.rglob("test/**/*.*js") if "node_modules" not in p.parts]
if not tests:
    print("FAIL: no tests were added for the previously untested formatReport")
    sys.exit(1)
suite = subprocess.run(["node", "--test"], cwd=WORKDIR, capture_output=True, text=True, timeout=120)
if suite.returncode != 0:
    print("FAIL: test suite does not pass")
    print((suite.stdout + suite.stderr)[-800:])
    sys.exit(1)

src = (FIXTURE / "src/report.js").read_text()
MUTANTS = {
    "counts-login": src.replace('e.kind == "export"', 'e.kind == "export" || e.kind == "login"'),
    "no-overage-line": re.sub(r"if \(total > user\.quota\)", "if (false)", src),
    "pct-floor": src.replace("Math.round(", "Math.floor("),
    "default-name": src.replace('"there"', '"friend"'),
}
survivors = []
with tempfile.TemporaryDirectory() as tmp:
    for name, body in MUTANTS.items():
        d = Path(tmp) / name
        shutil.copytree(WORKDIR, d, ignore=shutil.ignore_patterns("node_modules", ".git"))
        target = d / "src/report.js"
        target.write_text(body)
        if subprocess.run(["node", "--test"], cwd=d, capture_output=True, timeout=120).returncode == 0:
            survivors.append(name)
if len(survivors) > 1:
    print(f"FAIL: tests miss behavior changes: {', '.join(survivors)}")
    sys.exit(1)
print(f"PASS: behavior preserved; tests catch {len(MUTANTS) - len(survivors)}/{len(MUTANTS)} behavior changes")
