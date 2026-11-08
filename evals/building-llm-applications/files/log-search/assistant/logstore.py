"""Access to the service's application logs."""

from __future__ import annotations

import os
from pathlib import Path

LOG_PATH = Path(os.environ.get("APP_LOG_PATH", "/var/log/app/app.log"))


def read_lines() -> list[str]:
    """All log lines, oldest first. Each line is `<ISO timestamp> <LEVEL> <service> <message>`."""
    return LOG_PATH.read_text(encoding="utf-8").splitlines()
