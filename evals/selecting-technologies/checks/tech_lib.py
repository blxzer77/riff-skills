"""Shared helpers for selecting-technologies eval checks.

Facts that age (release dates, end-of-life, deprecations) are read from a pinned
snapshot under `data/`, with the source URL and retrieval date recorded there, so a
grade does not depend on network access or on when it is run.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import venv
from datetime import date
from pathlib import Path

WORKDIR = Path(os.environ["EVAL_WORKDIR"])
FIXTURE = Path(os.environ["EVAL_FIXTURE"])
DATA = Path(__file__).resolve().parent / "data"

# The day the snapshots were taken; "supported" is judged as of this date.
AS_OF = date(2026, 11, 2)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def ok(message: str) -> None:
    print(f"PASS: {message}")
    sys.exit(0)


def requirement_names(path: Path) -> dict[str, str]:
    """Map normalized distribution name -> full requirement line."""
    found = {}
    if not path.is_file():
        return found
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        name = re.split(r"[\s\[<>=!~;@]", line, maxsplit=1)[0]
        found[re.sub(r"[-_.]+", "-", name).lower()] = line
    return found


def added_requirements(name: str = "requirements.txt") -> dict[str, str]:
    before = requirement_names(FIXTURE / name)
    after = requirement_names(WORKDIR / name)
    return {k: v for k, v in after.items() if k not in before}


def python_files(root: Path) -> list[Path]:
    skip = {".git", ".venv", "venv", "node_modules", "__pycache__"}
    return [p for p in sorted(root.rglob("*.py")) if not skip & set(p.relative_to(root).parts)]


def install_and_run(requirements: Path, *commands: list[str]) -> tuple[bool, str]:
    """Install requirements into a fresh venv, then run each command in WORKDIR with
    that venv's python. Stops at the first failure."""
    with tempfile.TemporaryDirectory(prefix="tech-check-") as tmp:
        env_dir = Path(tmp) / "venv"
        venv.create(env_dir, with_pip=True)
        py = env_dir / "bin" / "python"
        if requirements.is_file() and requirement_names(requirements):
            proc = subprocess.run([str(py), "-m", "pip", "install", "-q", "--disable-pip-version-check",
                                   "-r", str(requirements)], capture_output=True, text=True, timeout=240)
            if proc.returncode != 0:
                return False, "pip install failed: " + (proc.stdout + proc.stderr)[-800:]
        # Probes and tests run without network so a test that calls a live service fails.
        run_env = {k: v for k, v in os.environ.items() if "proxy" not in k.lower()}
        offline = ["unshare", "-rn"] if shutil.which("unshare") else []
        output = ""
        for cmd in commands:
            proc = subprocess.run([*offline, str(py), *cmd], cwd=WORKDIR, capture_output=True,
                                  text=True, timeout=240, env=run_env)
            output = (proc.stdout + proc.stderr)[-1500:]
            if proc.returncode != 0:
                return False, f"{' '.join(cmd)}: {output}"
        return True, output


def last_release(name: str) -> str | None:
    """Last PyPI release date (YYYY-MM-DD) on or before AS_OF.

    Reads the pinned snapshot first; names not in it are fetched from PyPI and
    filtered to releases on or before AS_OF so the answer does not drift.
    """
    snap = json.loads((DATA / "pypi-last-release.json").read_text(encoding="utf-8"))["packages"]
    if snap.get(name):
        return snap[name]["last_release"]
    import urllib.request
    try:
        with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/json", timeout=30) as resp:
            data = json.load(resp)
    except Exception:
        return None
    dates = sorted(f[0]["upload_time"][:10] for f in data["releases"].values() if f)
    dates = [d for d in dates if d <= AS_OF.isoformat()]
    return dates[-1] if dates else None


def node_schedule() -> dict[int, dict]:
    raw = json.loads((DATA / "node-release-schedule.json").read_text(encoding="utf-8"))
    out = {}
    for key, value in raw.items():
        major = key.lstrip("v").split(".")[0]
        if major.isdigit() and key.lstrip("v") == major:
            out[int(major)] = value
    return out


def node_supported(major: int) -> bool:
    """True when the release line is LTS and has not reached end of life as of AS_OF.

    Node.js: production applications should use only Active LTS or Maintenance LTS.
    """
    rel = node_schedule().get(major)
    if rel is None or not rel.get("lts"):
        return False
    start = date.fromisoformat(rel["lts"])
    end = date.fromisoformat(rel["end"])
    return start <= AS_OF < end
