"""Shared import analysis for designing-modules eval checks.

Parses every Python file under `shop/` with `ast` and records which top-level module
(`shop.<name>`) imports which, including imports inside functions, so a deferred
import does not hide a dependency.
"""

from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

WORKDIR = Path(os.environ["EVAL_WORKDIR"])
PACKAGE = WORKDIR / "shop"


def module_of(path: Path) -> str:
    rel = path.relative_to(WORKDIR).with_suffix("")
    parts = [p for p in rel.parts if p != "__init__"]
    return ".".join(parts)


def owner(dotted: str) -> str | None:
    parts = dotted.split(".")
    return ".".join(parts[:2]) if len(parts) >= 2 and parts[0] == "shop" else None


def imports() -> list[tuple[str, str, int, Path]]:
    """(importing module, imported dotted name, line, file) for every import."""
    found = []
    for path in sorted(PACKAGE.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        here = module_of(path)
        package = here if path.name == "__init__.py" else here.rsplit(".", 1)[0]
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    found.append((here, alias.name, node.lineno, path))
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    base = package.split(".")
                    base = base[: len(base) - (node.level - 1)]
                    target = ".".join(base + ([node.module] if node.module else []))
                else:
                    target = node.module or ""
                found.append((here, target, node.lineno, path))
                for alias in node.names:
                    found.append((here, f"{target}.{alias.name}", node.lineno, path))
    return found


def top_modules() -> set[str]:
    return {f"shop.{p.name}" for p in PACKAGE.iterdir()
            if (p.is_dir() and (p / "__init__.py").exists()) or (p.suffix == ".py" and p.stem != "__init__")}


def internal_violations() -> list[str]:
    """Imports of `shop.X.internal...` from outside module `shop.X`."""
    bad = []
    for here, target, line, path in imports():
        parts = target.split(".")
        if len(parts) >= 3 and parts[0] == "shop" and parts[2] in ("internal", "_internal", "private"):
            if owner(here) != ".".join(parts[:2]):
                bad.append(f"{path.relative_to(WORKDIR)}:{line} imports {target}")
    return sorted(set(bad))


def module_graph() -> dict[str, set[str]]:
    modules = top_modules()
    graph = {m: set() for m in modules}
    for here, target, _, _ in imports():
        a, b = owner(here), owner(target)
        if a in modules and b in modules and a != b:
            graph[a].add(b)
    return graph


def find_cycle(graph: dict[str, set[str]]) -> list[str] | None:
    state, stack = {}, []

    def visit(node):
        state[node] = 1
        stack.append(node)
        for nxt in sorted(graph.get(node, ())):
            if state.get(nxt) == 1:
                return stack[stack.index(nxt):] + [nxt]
            if state.get(nxt) is None:
                cycle = visit(nxt)
                if cycle:
                    return cycle
        stack.pop()
        state[node] = 2
        return None

    for node in sorted(graph):
        if state.get(node) is None:
            cycle = visit(node)
            if cycle:
                return cycle
    return None


def run_tests() -> tuple[bool, str]:
    proc = subprocess.run([sys.executable, "-m", "unittest", "-q"], cwd=WORKDIR,
                          capture_output=True, text=True, timeout=120)
    return proc.returncode == 0, (proc.stdout + proc.stderr)[-600:]


GRAB_BAG_NAMES = {"utils", "util", "common", "shared", "helpers", "lib", "core", "misc"}


def grab_bag_modules() -> list[str]:
    return sorted(m for m in top_modules() if m.split(".")[1] in GRAB_BAG_NAMES)
