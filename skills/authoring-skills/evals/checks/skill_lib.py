"""Shared helpers for authoring-skills eval checks. Requires PyYAML."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import yaml

WORKDIR = Path(os.environ.get("EVAL_WORKDIR", "."))
SPEC_FIELDS = {"name", "description", "license", "compatibility", "metadata"}
VENDOR_PATTERNS = [
    r"\bAskUserQuestion\b", r"\bTodoWrite\b", r"\bthe (Bash|Read|Edit|Write) tool\b",
    r"\$\{CLAUDE_[A-Z_]+\}", r"\bCLAUDE_PLUGIN_ROOT\b", r"\bClaude\b", r"\bCodex\b",
]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def ok(msg: str) -> None:
    print(f"PASS: {msg}")
    sys.exit(0)


def load_skill(skill_dir: Path) -> tuple[dict, str]:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        fail(f"{skill_dir}/SKILL.md has no frontmatter")
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as exc:
        fail(f"frontmatter is invalid YAML: {exc}")
    return fm, m.group(2)


def check_portable(skill_dir: Path) -> None:
    fm, body = load_skill(skill_dir)
    extra = set(fm) - SPEC_FIELDS
    if extra:
        fail(f"non-portable frontmatter fields: {sorted(extra)}")
    if fm.get("name") != skill_dir.name:
        fail(f"name {fm.get('name')!r} does not match directory {skill_dir.name!r}")
    desc = " ".join(str(fm.get("description", "")).split())
    if not 40 <= len(desc) <= 1024 or "Use when" not in desc:
        fail(f"description must be 40-1024 chars and contain 'Use when': {desc[:120]!r}")
    texts = [desc, body] + [p.read_text(encoding="utf-8") for p in skill_dir.rglob("*.md") if p.name != "SKILL.md"]
    for pat in VENDOR_PATTERNS:
        for t in texts:
            if re.search(pat, t):
                fail(f"vendor-specific reference matches {pat!r}")
    if body.count("\n") > 500:
        fail("SKILL.md body exceeds 500 lines")
