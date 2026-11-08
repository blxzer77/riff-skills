#!/usr/bin/env python3
"""Log search tool eval: responses are bounded, say when they are cut, and errors are usable.

Imports `assistant.log_tools` (which must register a tool named `search_logs`), points
the log store at a 10,000-line fixture with 3,000 matching lines, and checks:
  1. a broad query returns a string well under the size of all matches;
  2. that response tells the model results were cut or how many exist;
  3. a call missing its required argument returns an error string, not an exception.
"""

import importlib
import os
import re
import sys
import tempfile
from pathlib import Path

workdir = Path(os.environ["EVAL_WORKDIR"])
sys.path.insert(0, str(workdir))

MAX_CHARS = 20_000  # all 3,000 matches are ~300,000 characters

with tempfile.TemporaryDirectory() as tmp:
    log = Path(tmp) / "app.log"
    lines = []
    for i in range(10_000):
        level = "ERROR" if i % 10 < 3 else "INFO"
        lines.append(f"2026-10-31T12:{i // 600 % 60:02d}:{i % 60:02d}Z {level} payments "
                     f"request {i:05d} for order ORD-{i:06d} took {i % 900} ms")
    log.write_text("\n".join(lines), encoding="utf-8")
    os.environ["APP_LOG_PATH"] = str(log)

    try:
        tools = importlib.import_module("assistant.tools")
        logstore = importlib.import_module("assistant.logstore")
        logstore.LOG_PATH = log
        importlib.import_module("assistant.log_tools")
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: could not import assistant.log_tools: {exc!r}")
        sys.exit(1)

    definitions = {d.get("name"): d for d in tools.definitions()}
    if "search_logs" not in definitions:
        print(f"FAIL: no tool named search_logs registered; registered: {list(definitions)}")
        sys.exit(1)

    # The prompt names no parameter, so read the search-string parameter from the
    # tool's own schema instead of assuming one.
    definition = definitions["search_logs"]
    schema = (definition.get("input_schema") or definition.get("parameters")
              or definition.get("inputSchema") or {})
    properties = schema.get("properties") or {}
    strings = [n for n, p in properties.items() if isinstance(p, dict) and p.get("type") == "string"]
    required = [n for n in schema.get("required") or [] if n in strings]
    param = (required or strings or ["query"])[0]

    try:
        result = tools.call("search_logs", {param: "ERROR"})
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: search_logs raised on a normal query: {exc!r}")
        sys.exit(1)
    if not isinstance(result, str):
        print(f"FAIL: search_logs returned {type(result).__name__}, expected str")
        sys.exit(1)
    if len(result) > MAX_CHARS:
        print(f"FAIL: unbounded response: {len(result)} chars for 3,000 matches")
        sys.exit(1)
    if not re.search(r"truncat|more (results|matches|lines)|showing|of 3[,.]?000|3[,.]?000 (matches|results|lines)"
                     r"|next_page|page_token|offset|cursor|narrow", result, re.IGNORECASE):
        print("FAIL: response is cut but does not tell the model that results were truncated "
              f"or how many exist; first 300 chars: {result[:300]!r}")
        sys.exit(1)

    try:
        error = tools.call("search_logs", {})
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: missing argument raised {exc!r} instead of returning an error the model can act on")
        sys.exit(1)
    if not isinstance(error, str) or not error.strip():
        print(f"FAIL: missing argument returned {error!r}")
        sys.exit(1)

print(f"PASS: bounded response ({len(result)} chars, parameter {param!r}) with truncation "
      "notice; missing argument returns an error message")
