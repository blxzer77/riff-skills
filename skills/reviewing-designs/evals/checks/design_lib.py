"""Shared helpers for reviewing-designs eval checks.

The prompts do not prescribe an output format, so checks do not parse headings or
severity labels. They test whether the review names the project fact that decides
the case, using patterns that accept different wordings of the same fact.
"""

from __future__ import annotations

import os
import re
from pathlib import Path


def response_text() -> str:
    return Path(os.environ["EVAL_RESPONSE"]).read_text(encoding="utf-8", errors="replace")


def missing(text: str, patterns: list[str]) -> list[str]:
    """Patterns (case-insensitive regexes) that do not occur in the text.

    `.` does not cross line breaks, so a pattern joining two terms matches only when
    they appear in the same line or paragraph line, not anywhere in the response.
    """
    flat = text.replace("’", "'").replace("`", "")
    return [p for p in patterns if not re.search(p, flat, re.IGNORECASE)]
