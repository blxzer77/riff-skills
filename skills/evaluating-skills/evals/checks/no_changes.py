#!/usr/bin/env python3
"""Pass when the agent left the fixture unchanged."""
import os, sys
from pathlib import Path

def main():
    work = Path(os.environ["EVAL_WORKDIR"]); fixture = Path(os.environ["EVAL_FIXTURE"])
    def files(root): return {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    if files(work) != files(fixture): print("FAIL: working artifact changed"); return 1
    print("PASS: no files modified"); return 0
if __name__ == "__main__": sys.exit(main())
