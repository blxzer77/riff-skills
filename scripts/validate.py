#!/usr/bin/env python3
"""Validate riff-skills against the Agent Skills spec and this repository's conventions.

Checks every directory under skills/ (or the paths given):
  spec       frontmatter fields, name and description rules, name == directory
  repo       vendor-neutral frontmatter, reserved words, description shape,
             body length, local file references, evals files, marketplace listing

Exit codes: 0 = no errors, 1 = errors found, 2 = usage error.
Requires PyYAML (the same parser family most agent clients use).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("error: PyYAML is required (pip install pyyaml)")

REPO = Path(__file__).resolve().parent.parent
SPEC_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
REPO_FIELDS = {"name", "description", "license", "compatibility", "metadata"}
RESERVED = ("anthropic", "claude", "openai", "codex", "gemini")
MAX_BODY_LINES = 500
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
# Backticked paths are checked only in SKILL.md, where they name the skill's own files;
# in references they often describe another skill's layout.
CODE_PATH_RE = re.compile(r"`((?:references|scripts|assets)/[^`\s]+)`")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"{where}: {msg}")


def split_frontmatter(text: str) -> tuple[str | None, str]:
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end + 5 :]


def check_skill(skill_dir: Path, rep: Report) -> str | None:
    where = str(skill_dir.relative_to(REPO)) if skill_dir.is_relative_to(REPO) else str(skill_dir)
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        rep.error(where, "SKILL.md not found")
        return None
    text = skill_md.read_text(encoding="utf-8")
    raw, body = split_frontmatter(text)
    if raw is None:
        rep.error(f"{where}/SKILL.md", "missing YAML frontmatter delimited by '---' lines at the top")
        return None
    try:
        fm = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        rep.error(f"{where}/SKILL.md", f"frontmatter is not valid YAML: {exc}")
        return None
    if not isinstance(fm, dict):
        rep.error(f"{where}/SKILL.md", "frontmatter must be a mapping")
        return None

    unknown = set(fm) - SPEC_FIELDS
    if unknown:
        rep.error(where, f"fields outside the Agent Skills spec: {', '.join(sorted(unknown))}")
    extra = (set(fm) & SPEC_FIELDS) - REPO_FIELDS
    if extra:
        rep.error(where, f"experimental fields are not used in this repo: {', '.join(sorted(extra))}")
    if re.search(r"^\s*[\w-]+:\s*\[", raw, re.M):
        rep.warn(where, "flow-style list in frontmatter; strict YAML parsers reject it")

    name = fm.get("name")
    if not isinstance(name, str) or not name:
        rep.error(where, "name is required and must be a string")
        name = None
    else:
        name = unicodedata.normalize("NFKC", name)
        if len(name) > 64 or not NAME_RE.match(name):
            rep.error(where, f"name '{name}' must be 1-64 chars of a-z, 0-9 and single hyphens")
        if name != skill_dir.name:
            rep.error(where, f"name '{name}' must match directory name '{skill_dir.name}'")
        for word in RESERVED:
            if word in name.split("-"):
                rep.error(where, f"name contains vendor word '{word}'")

    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        rep.error(where, "description is required and must be a non-empty string")
    else:
        desc = " ".join(desc.split())
        if len(desc) > 1024:
            rep.error(where, f"description is {len(desc)} chars; maximum is 1024")
        if "<" in desc or ">" in desc:
            rep.error(where, "description must not contain angle brackets")
        if "Use when" not in desc:
            rep.error(where, "description must state when to use the skill ('Use when ...')")
        if re.match(r"^(I|We|You)\b", desc):
            rep.error(where, "description must be in third person")

    comp = fm.get("compatibility")
    if comp is not None and (not isinstance(comp, str) or not 1 <= len(comp) <= 500):
        rep.error(where, "compatibility must be a string of 1-500 chars")
    meta = fm.get("metadata")
    if meta is not None and (
        not isinstance(meta, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in meta.items())
    ):
        rep.error(where, "metadata must map strings to strings (quote dates and numbers)")

    body_lines = body.count("\n") + 1
    if body_lines > MAX_BODY_LINES:
        rep.error(where, f"SKILL.md body is {body_lines} lines; keep it under {MAX_BODY_LINES}")

    check_references(skill_dir, where, rep)
    check_evals(skill_dir, where, name, rep)
    return name


def check_references(skill_dir: Path, where: str, rep: Report) -> None:
    md_files = [skill_dir / "SKILL.md", *sorted((skill_dir / "references").glob("*.md"))]
    for md in md_files:
        text = md.read_text(encoding="utf-8")
        targets = [m.group(1) for m in LINK_RE.finditer(text)]
        if md.name == "SKILL.md":
            targets += [m.group(1) for m in CODE_PATH_RE.finditer(text)]
        for target in targets:
            if re.match(r"^[a-z]+://", target) or target.startswith("mailto:"):
                continue
            if "<" in target or "*" in target:
                continue
            resolved = skill_dir / target if md.name == "SKILL.md" else md.parent / target
            if not resolved.exists():
                rep.error(f"{where}/{md.relative_to(skill_dir)}", f"referenced path does not exist: {target}")
    for ref in sorted((skill_dir / "references").glob("**/*")):
        if ref.is_file() and ref.parent != skill_dir / "references":
            rep.warn(where, f"nested reference {ref.relative_to(skill_dir)}; keep references one level deep")
        if ref.suffix == ".md" and ref.is_file():
            lines = ref.read_text(encoding="utf-8").splitlines()
            if len(lines) > 100 and not any("contents" in l.lower() for l in lines[:12]):
                rep.warn(where, f"{ref.relative_to(skill_dir)} has {len(lines)} lines and no contents list near the top")


def check_evals(skill_dir: Path, where: str, name: str | None, rep: Report) -> None:
    evals = skill_dir / "evals" / "evals.json"
    if not evals.is_file():
        rep.warn(where, "no evals/evals.json")
    else:
        try:
            data = json.loads(evals.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            rep.error(f"{where}/evals/evals.json", f"invalid JSON: {exc}")
        else:
            if name and data.get("skill_name") != name:
                rep.error(f"{where}/evals/evals.json", "skill_name must equal the skill name")
            cases = data.get("evals", [])
            if len(cases) < 3:
                rep.warn(where, f"evals.json has {len(cases)} case(s); aim for at least 3")
            ids = [c.get("id") for c in cases]
            if len(ids) != len(set(ids)):
                rep.error(f"{where}/evals/evals.json", "duplicate eval ids")
            for c in cases:
                for key in ("id", "prompt", "expected_output"):
                    if key not in c:
                        rep.error(f"{where}/evals/evals.json", f"eval {c.get('id')} missing '{key}'")
                for f in c.get("files", []):
                    if not (skill_dir / f).exists():
                        rep.error(f"{where}/evals/evals.json", f"eval {c.get('id')} file not found: {f}")
                for a in c.get("assertions", []):
                    if isinstance(a, dict) and "script" in a and not (skill_dir / a["script"]).is_file():
                        rep.error(f"{where}/evals/evals.json", f"assertion script not found: {a['script']}")
    queries = skill_dir / "evals" / "trigger-queries.json"
    if not queries.is_file():
        rep.warn(where, "no evals/trigger-queries.json")
        return
    try:
        qs = json.loads(queries.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        rep.error(f"{where}/evals/trigger-queries.json", f"invalid JSON: {exc}")
        return
    pos = sum(1 for q in qs if q.get("should_trigger") is True)
    neg = sum(1 for q in qs if q.get("should_trigger") is False)
    if pos + neg != len(qs):
        rep.error(f"{where}/evals/trigger-queries.json", "every query needs a boolean should_trigger")
    if pos < 5 or neg < 5:
        rep.warn(where, f"trigger-queries.json has {pos} positive / {neg} negative; aim for 8-12 each")
    if any(q.get("set") not in ("train", "validation") for q in qs):
        rep.warn(where, "some trigger queries have no train/validation set; run split_queries.py")


def check_marketplace(names: set[str], rep: Report) -> None:
    path = REPO / ".claude-plugin" / "marketplace.json"
    if not path.is_file():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    listed: set[str] = set()
    for plugin in data.get("plugins", []):
        for s in plugin.get("skills", []):
            p = (REPO / s).resolve()
            if not (p / "SKILL.md").is_file():
                rep.error("marketplace.json", f"listed skill path has no SKILL.md: {s}")
            listed.add(p.name)
    for missing in sorted(names - listed):
        rep.error("marketplace.json", f"skill not listed: {missing}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", type=Path, help="skill directories (default: all under skills/)")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = ap.parse_args()

    dirs = [p.resolve() for p in args.paths] or sorted(p for p in (REPO / "skills").iterdir() if p.is_dir())
    if not dirs:
        print("error: no skill directories found", file=sys.stderr)
        return 2
    rep = Report()
    names = {n for d in dirs if (n := check_skill(d, rep))}
    if not args.paths:
        check_marketplace(names, rep)

    for w in rep.warnings:
        print(f"warning: {w}")
    for e in rep.errors:
        print(f"error: {e}")
    failed = bool(rep.errors) or (args.strict and bool(rep.warnings))
    print(f"{len(dirs)} skill(s) checked: {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
