#!/usr/bin/env python3
"""Pass when every Claude model ID in non-test code is active on the snapshot date.

Model status comes from data/claude-model-status.json (official model-deprecations
page, dated). A dateless alias such as `claude-sonnet-4-5` resolves to its dated
snapshot, so it takes that snapshot's status. Retired, deprecated (retirement
scheduled), and unknown IDs fail: an ID absent from the official table was most
likely recalled from memory and may not exist. Bedrock/Vertex-style IDs are judged
on the underlying Claude API name.
"""

import json
import re

from tech_lib import DATA, WORKDIR, fail, ok, python_files

ID = re.compile(r"""(?:["'=]\s*|\b)(?:[\w.-]*?anthropic\.)?(claude-[a-z0-9][\w.-]*?)(?:-v\d+(?::\d+)?)?(?:@\d{8})?(?=["'\s]|$)""",
                re.M)


def status_table() -> dict[str, str]:
    models = json.loads((DATA / "claude-model-status.json").read_text(encoding="utf-8"))["models"]
    table = {mid: info["status"] for mid, info in models.items()}
    for mid, info in models.items():
        alias = re.sub(r"-\d{8}$", "", mid)
        if alias != mid and alias not in table:
            table[alias] = info["status"]
    return table


CONFIG = {".toml", ".yaml", ".yml", ".json", ".cfg", ".ini", ".env"}


def sources():
    for path in python_files(WORKDIR):
        if "tests" not in path.relative_to(WORKDIR).parts and not path.name.startswith("test"):
            yield path
    for path in WORKDIR.rglob("*"):
        if path.is_file() and ".git" not in path.parts and (path.suffix in CONFIG or path.name.startswith(".env")):
            yield path


table = status_table()
found = {}
for path in sources():
    for m in ID.finditer(path.read_text(encoding="utf-8", errors="replace")):
        found.setdefault(m.group(1), f"{path.relative_to(WORKDIR)}")
if not found:
    fail("no Claude model ID found in non-test code")

bad = {mid: table.get(mid, "unknown") for mid in found if table.get(mid) != "active"}
if bad:
    fail("model ID(s) not active on the snapshot date: "
         + "; ".join(f"{mid} ({status}) in {found[mid]}" for mid, status in bad.items()))
ok("active model ID(s): " + ", ".join(f"{mid} in {where}" for mid, where in sorted(found.items())))
