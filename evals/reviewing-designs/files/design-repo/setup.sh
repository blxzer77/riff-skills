#!/usr/bin/env bash
# Leaves an uncommitted code change so "this code diff" has something to review.
# Removed from the sandbox before the agent runs.
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
p = Path("app/loans.py")
s = p.read_text()
s = s.replace("LOAN_DAYS = 21", "LOAN_DAYS = 28")
s = s.replace('if row is None or row[0]:', 'if row is None:')
p.write_text(s)
PY
