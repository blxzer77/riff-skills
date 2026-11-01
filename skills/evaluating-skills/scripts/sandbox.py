"""Fresh per-run working directories, kept outside the repository under test."""

from __future__ import annotations

import os
import shutil
import subprocess
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


SETUP_SCRIPT = "setup.sh"


@contextmanager
def sandbox(root: Path, fixture: Path | None = None):
    """Yield a git-initialized working directory with the fixture committed; delete it after.

    If the fixture contains `setup.sh`, it runs after the initial commit (with git
    identity configured) and is then removed, so a fixture can stage changes, create
    branches, or leave uncommitted edits without the agent seeing the script.
    """
    base = Path(root).expanduser() / uuid.uuid4().hex[:12]
    workdir = base / "work"
    workdir.mkdir(parents=True)
    try:
        if fixture is not None and fixture.is_dir():
            shutil.copytree(fixture, workdir, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns(SETUP_SCRIPT))
        git(["init", "-q", "-b", "main"], workdir)
        git(["add", "-A"], workdir)
        git(["commit", "-q", "--no-gpg-sign", "--allow-empty", "-m", "fixture"], workdir)
        setup = fixture / SETUP_SCRIPT if fixture is not None else None
        if setup is not None and setup.is_file():
            env = dict(os.environ, GIT_AUTHOR_NAME="dev", GIT_AUTHOR_EMAIL="dev@localhost",
                       GIT_COMMITTER_NAME="dev", GIT_COMMITTER_EMAIL="dev@localhost",
                       GIT_CONFIG_GLOBAL="/dev/null")
            proc = subprocess.run(["bash", str(setup.resolve())], cwd=workdir, env=env,
                                  capture_output=True, text=True, timeout=120)
            if proc.returncode != 0:
                raise HarnessError(f"fixture setup failed: {proc.stderr[-500:]}")
        yield workdir
    finally:
        shutil.rmtree(base, ignore_errors=True)


def diff_against_fixture(workdir: Path) -> str:
    git(["add", "-A"], workdir)
    return git(["diff", "--cached", "--binary", "HEAD"], workdir)
