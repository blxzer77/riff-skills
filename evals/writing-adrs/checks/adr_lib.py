"""Shared helpers for writing-adrs eval checks. Standard library only."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

WORKDIR = Path(os.environ.get("EVAL_WORKDIR", "."))
FIXTURE = Path(os.environ.get("EVAL_FIXTURE", "."))


def new_files(subdir: str) -> list[Path]:
    """Markdown files under subdir that exist in the workdir but not in the fixture."""
    root = WORKDIR / subdir
    if not root.is_dir():
        return []
    out = []
    for p in sorted(root.glob("*.md")):
        if not (FIXTURE / subdir / p.name).exists():
            out.append(p)
    return out


def sections(text: str) -> dict[str, str]:
    """Map lowercase heading text (any level) to the body below it."""
    parts = re.split(r"^#{1,6}\s+(.+?)\s*$", text, flags=re.M)
    return {parts[i].strip().lower(): parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def find_section(secs: dict[str, str], *keys: str) -> str | None:
    for heading, body in secs.items():
        if any(k in heading for k in keys):
            return body
    return None


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def ok(msg: str) -> None:
    print(f"PASS: {msg}")
    sys.exit(0)
