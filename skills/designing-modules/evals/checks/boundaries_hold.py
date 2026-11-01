#!/usr/bin/env python3
"""Pass when no module imports another module's internals, modules form no import
cycle (counting imports inside functions), and the test suite passes."""

import sys

from module_lib import find_cycle, internal_violations, module_graph, run_tests

problems = []
violations = internal_violations()
if violations:
    problems.append("imports of another module's internals: " + "; ".join(violations[:6]))
cycle = find_cycle(module_graph())
if cycle:
    problems.append("import cycle between modules: " + " -> ".join(cycle))
ok, output = run_tests()
if not ok:
    problems.append("test suite fails: " + output.strip().splitlines()[-1] if output.strip() else "test suite fails")
if problems:
    print("FAIL: " + " | ".join(problems))
    sys.exit(1)
print("PASS: no cross-module internal imports, no module cycle, tests pass")
