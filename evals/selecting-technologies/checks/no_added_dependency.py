#!/usr/bin/env python3
"""Pass when the change adds no third-party dependency and no new decision document.

For a small addition that the existing stack already covers, adding a second library
for the same job or writing an ADR is over-application of a selection process.
"""

from tech_lib import FIXTURE, WORKDIR, added_requirements, fail, ok

added = added_requirements()
new_docs = sorted(str(p.relative_to(WORKDIR)) for p in WORKDIR.rglob("*.md")
                  if ".git" not in p.parts and not (FIXTURE / p.relative_to(WORKDIR)).exists())
problems = []
if added:
    problems.append(f"dependencies added: {sorted(added.values())}")
if new_docs:
    problems.append(f"new documents added: {new_docs}")
if problems:
    fail("; ".join(problems))
ok("no new dependency and no new decision document")
