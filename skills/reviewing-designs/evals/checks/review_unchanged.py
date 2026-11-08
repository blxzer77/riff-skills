#!/usr/bin/env python3
"""Design review eval: the reviewer must leave the supplied project unchanged."""

import os
import sys
from pathlib import Path

workdir = Path(os.environ["EVAL_WORKDIR"])
fixture = Path(os.environ["EVAL_FIXTURE"])


def files(root):
    result = {}
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part in {".git", "__pycache__", ".pytest_cache", "node_modules"} for part in relative.parts):
            continue
        if path.is_file():
            result[relative.as_posix()] = path.read_bytes()
    return result


expected = files(fixture)
actual = files(workdir)
if expected != actual:
    changed = sorted(set(expected) | set(actual))
    changed = [path for path in changed if expected.get(path) != actual.get(path)]
    print("FAIL: review changed the supplied worktree:")
    print("\n".join(changed[-40:]))
    sys.exit(1)
print("PASS: review worktree is unchanged")
