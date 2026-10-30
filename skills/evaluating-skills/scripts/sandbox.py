"""Fresh per-run working directories, kept outside the repository under test."""

from __future__ import annotations

import shutil
import uuid
from contextlib import contextmanager
from pathlib import Path

from common import HarnessError, git

DEFAULT_ROOT = Path.home() / ".cache" / "riff-skills" / "runs"


def copy_fixture(skill_dir: Path, files: list[str], dest: Path) -> None:
    """Copy eval input files into `dest`: files by basename, directories by contents."""
    dest.mkdir(parents=True, exist_ok=True)
    root = Path(skill_dir).resolve()
    for rel in files or []:
        src = (root / rel).resolve()
        if root not in src.parents and src != root:
            raise HarnessError(f"eval file {rel!r} escapes the skill directory")
        if src.is_dir():
            shutil.copytree(src, dest, dirs_exist_ok=True)
        elif src.is_file():
            shutil.copy2(src, dest / src.name)
        else:
            raise HarnessError(f"eval file not found: {rel}")


@contextmanager
def sandbox(root: Path, fixture: Path | None = None):
    """Yield a git-initialized working directory with the fixture committed; delete it after."""
    base = Path(root).expanduser() / uuid.uuid4().hex[:12]
    workdir = base / "work"
    workdir.mkdir(parents=True)
    try:
        if fixture is not None and fixture.is_dir():
            shutil.copytree(fixture, workdir, dirs_exist_ok=True)
        git(["init", "-q", "-b", "main"], workdir)
        git(["add", "-A"], workdir)
        git(["commit", "-q", "--no-gpg-sign", "--allow-empty", "-m", "fixture"], workdir)
        yield workdir
    finally:
        shutil.rmtree(base, ignore_errors=True)


def diff_against_fixture(workdir: Path) -> str:
    git(["add", "-A"], workdir)
    return git(["diff", "--cached", "--binary", "HEAD"], workdir)
