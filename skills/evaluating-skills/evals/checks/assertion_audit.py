#!/usr/bin/env python3
"""Validate the repaired assertion audit against the artifacts it claims to repair."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

WORKDIR = Path(os.environ["EVAL_WORKDIR"]).resolve()


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def run_check(script: Path, response: Path, args: list[str]) -> bool:
    env = dict(os.environ, EVAL_WORKDIR=str(WORKDIR), EVAL_RESPONSE=str(response),
               EVAL_FIXTURE=str(os.environ.get("EVAL_FIXTURE", WORKDIR)))
    proc = subprocess.run([sys.executable, str(script), *args], cwd=WORKDIR,
                          env=env, capture_output=True, text=True, timeout=30)
    return proc.returncode == 0


def main() -> None:
    spec_path = WORKDIR / "eval.json"
    if not spec_path.is_file():
        fail("repaired eval.json is missing")
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"repaired eval.json is invalid: {exc}")

    assertions = spec.get("assertions")
    if not isinstance(assertions, list) or len(assertions) < 2:
        fail("repaired eval.json has fewer than two assertions")
    ids = [a.get("id") for a in assertions if isinstance(a, dict)]
    if len(ids) != len(assertions) or not all(isinstance(i, str) and i for i in ids):
        fail("repaired assertions need non-empty stable string IDs")
    if len(set(ids)) != len(ids):
        fail("repaired assertion IDs are not unique")
    scripts = []
    for assertion in assertions:
        script_name = assertion.get("script")
        if not isinstance(script_name, str):
            fail(f"assertion {assertion.get('id')} is not mechanically checked")
        script = (WORKDIR / script_name).resolve()
        if WORKDIR not in script.parents or not script.is_file():
            fail(f"assertion script is missing or escapes workdir: {script_name}")
        scripts.append((script, [str(x) for x in (assertion.get("args") or [])]))

    output_schema = str((spec.get("schema") or {}).get("output", "")).lower()
    assertion_text = " ".join(str(a.get("text", "")) for a in assertions).lower()
    if "finding" not in output_schema or "3" not in assertion_text:
        fail("repaired schema/assertions do not preserve the three-finding intent")

    artifacts = {p.stem: p for p in WORKDIR.glob("*.md")}
    required = {"good", "near-miss", "empty"}
    if not required <= artifacts.keys():
        fail(f"validation corpus is incomplete: missing {sorted(required - artifacts.keys())}")
    alternatives = [p for stem, p in artifacts.items() if stem not in required]
    if not alternatives:
        response = Path(os.environ["EVAL_RESPONSE"]).read_text(encoding="utf-8").lower()
        if not any(term in response for term in ("alternative", "different wording", "different format")):
            fail("neither an alternative artifact nor an alternative validation is documented")

    outcomes = {}
    for label, path in {"good": artifacts["good"], "near-miss": artifacts["near-miss"],
                        "empty": artifacts["empty"]}.items():
        outcomes[label] = [run_check(script, path, args) for script, args in scripts]
    alternative_outcomes = ([run_check(script, alternatives[0], args) for script, args in scripts]
                            if alternatives else None)

    if not all(outcomes["good"]):
        fail(f"good artifact fails repaired checks: {outcomes['good']}")
    if not any(not passed for passed in outcomes["near-miss"]):
        fail("near-miss artifact passes every repaired check")
    if not any(not passed for passed in outcomes["empty"]):
        fail("empty artifact passes every repaired check")
    if alternative_outcomes is not None and not all(alternative_outcomes):
        fail(f"correct alternative fails repaired checks: {alternative_outcomes}")
    print("PASS: repaired schema and scripts pass good and reject near-miss/empty; alternative validation is documented or executable")


if __name__ == "__main__":
    main()
