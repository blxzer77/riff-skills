"""Shared helpers for the eval scripts: skill metadata, evals.json, JSON I/O, git."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_KEY = re.compile(r"^([A-Za-z0-9_-]+):(?:\s+(.*)|\s*)$")


class HarnessError(RuntimeError):
    """A usage or input error that should stop the script with a clear message."""


def die(message: str, code: int = 2) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _split_frontmatter(text: str) -> tuple[list[str], int]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise HarnessError("SKILL.md does not start with '---' frontmatter")
    for end in range(1, len(lines)):
        if lines[end].strip() == "---":
            return lines, end
    raise HarnessError("SKILL.md frontmatter is not closed with '---'")


def _scalar(head: str, block: list[str]) -> str:
    head = head.strip()
    if head[:1] in (">", "|"):
        body = [line for line in block]
        indents = [len(l) - len(l.lstrip()) for l in body if l.strip()]
        cut = min(indents) if indents else 0
        body = [l[cut:] if l.strip() else "" for l in body]
        if head[0] == "|":
            return "\n".join(body).strip()
        paragraphs, current = [], []
        for line in body:
            if line:
                current.append(line.strip())
            elif current:
                paragraphs.append(" ".join(current))
                current = []
        if current:
            paragraphs.append(" ".join(current))
        return "\n".join(paragraphs).strip()
    if head.startswith('"'):
        joined = " ".join([head] + [l.strip() for l in block if l.strip()])
        try:
            return json.loads(joined)
        except json.JSONDecodeError:
            return joined.strip('"')
    if head.startswith("'"):
        joined = " ".join([head] + [l.strip() for l in block if l.strip()])
        return joined[1:-1].replace("''", "'") if joined.endswith("'") else joined[1:]
    return " ".join([head] + [l.strip() for l in block if l.strip()]).strip()


def read_frontmatter(skill_dir: Path) -> dict[str, str]:
    """Return `name` and `description` from SKILL.md (plain, quoted, `>` and `|` scalars)."""
    skill_md = Path(skill_dir) / "SKILL.md"
    if not skill_md.is_file():
        raise HarnessError(f"no SKILL.md in {skill_dir}")
    lines, end = _split_frontmatter(skill_md.read_text(encoding="utf-8"))
    body = lines[1:end]
    out: dict[str, str] = {}
    i = 0
    while i < len(body):
        match = _KEY.match(body[i])
        i += 1
        if not match:
            continue
        block = []
        while i < len(body) and (body[i][:1] in (" ", "\t") or not body[i].strip()):
            block.append(body[i])
            i += 1
        if match.group(1) in ("name", "description"):
            out[match.group(1)] = _scalar(match.group(2) or "", block)
    return out


def replace_description(skill_md: Path, description: str) -> None:
    """Rewrite the frontmatter `description` of one SKILL.md copy in place."""
    lines, end = _split_frontmatter(skill_md.read_text(encoding="utf-8"))
    out, i, replaced = lines[:1], 1, False
    while i < end:
        match = _KEY.match(lines[i])
        if match and match.group(1) == "description":
            out.append("description: " + json.dumps(description, ensure_ascii=False))
            replaced = True
            i += 1
            while i < end and (lines[i][:1] in (" ", "\t") or not lines[i].strip()):
                i += 1
            continue
        out.append(lines[i])
        i += 1
    if not replaced:
        out.append("description: " + json.dumps(description, ensure_ascii=False))
    out.extend(lines[end:])
    skill_md.write_text("\n".join(out) + "\n", encoding="utf-8")


def skill_name(skill_dir: Path) -> str:
    return read_frontmatter(skill_dir).get("name") or Path(skill_dir).resolve().name


def eval_dirname(ev: dict) -> str:
    return f"eval-{ev.get('name') or ev['id']}"


def load_evals(skill_dir: Path) -> list[dict]:
    path = Path(skill_dir) / "evals" / "evals.json"
    if not path.is_file():
        raise HarnessError(f"missing {path}")
    data = read_json(path)
    evals = data.get("evals") if isinstance(data, dict) else None
    if not isinstance(evals, list) or not evals:
        raise HarnessError(f"{path}: expected a non-empty 'evals' list")
    seen = set()
    for ev in evals:
        for key in ("id", "prompt", "expected_output"):
            if key not in ev:
                raise HarnessError(f"{path}: eval {ev.get('id', '?')} is missing '{key}'")
        dirname = eval_dirname(ev)
        if dirname in seen:
            raise HarnessError(f"{path}: duplicate eval directory name {dirname}")
        seen.add(dirname)
    return evals


def normalize_assertions(raw) -> list[dict]:
    out = []
    for item in raw or []:
        if isinstance(item, str):
            out.append({"text": item})
        elif isinstance(item, dict) and isinstance(item.get("text"), str):
            out.append(dict(item))
        else:
            raise HarnessError(f"invalid assertion: {item!r}")
    return out


def git(args: list[str], cwd: Path) -> str:
    proc = subprocess.run(
        ["git", "-c", "user.name=eval", "-c", "user.email=eval@localhost",
         "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *args],
        cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        raise HarnessError(f"git {' '.join(args)} failed in {cwd}: {proc.stderr.strip()}")
    return proc.stdout


def truncate(text: str, limit: int) -> tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    return text[:limit], True


def is_within(path: Path, parent: Path) -> bool:
    try:
        Path(path).resolve().relative_to(Path(parent).resolve())
        return True
    except ValueError:
        return False
