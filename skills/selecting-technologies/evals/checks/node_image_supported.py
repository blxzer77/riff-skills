#!/usr/bin/env python3
"""Pass when every Node.js base image in the added Dockerfile(s) is a supported LTS line.

Supported means Active or Maintenance LTS on the snapshot date (see tech_lib.AS_OF and
data/node-release-schedule.json). Numeric tags (`node:24-alpine`), release codenames
(`node:krypton`), `lts` tags, ARG defaults, and distroless `nodejsNN` images are
resolved. `latest`, `current`, and untagged `node` track the Current line, which the
Node.js project does not recommend for production, so they fail.
"""

import re

from tech_lib import WORKDIR, fail, node_schedule, node_supported, ok

FROM = re.compile(r"^\s*FROM\s+(?:--platform=\S+\s+)?(\S+)", re.IGNORECASE | re.MULTILINE)
ARG = re.compile(r"^\s*ARG\s+(\w+)=(\S+)", re.IGNORECASE | re.MULTILINE)


def dockerfiles():
    return [p for p in WORKDIR.rglob("*")
            if p.is_file() and ".git" not in p.parts and "node_modules" not in p.parts
            and (p.name == "Dockerfile" or p.name.startswith("Dockerfile.")
                 or p.name.endswith(".Dockerfile") or p.name == "Containerfile")]


def expand(ref: str, args: dict[str, str]) -> str:
    def sub(m):
        return args.get(m.group(1) or m.group(2), m.group(0))
    return re.sub(r"\$\{(\w+)(?::?-[^}]*)?\}|\$(\w+)", sub, ref)


def node_major(ref: str, codenames: dict[str, int]) -> tuple[int | None, str]:
    """Return (major, note) for a Node image reference, or (None, reason)."""
    name, _, tag = ref.partition("@")[0].partition(":")
    base = name.rsplit("/", 1)[-1]
    if base == "node":
        if not tag or tag in {"latest", "current"} or tag.startswith("current-"):
            return None, f"{ref}: tracks the Current line, not an LTS line"
        head = tag.split("-")[0]
        if head == "lts":
            return max(m for m in codenames.values() if node_supported(m)), f"{ref}: lts tag"
        if head.split(".")[0].isdigit():
            return int(head.split(".")[0]), ref
        if head in codenames:
            return codenames[head], f"{ref}: codename {head}"
        return None, f"{ref}: unrecognized node tag"
    m = re.match(r"nodejs(\d+)", base)
    if m:
        return int(m.group(1)), f"{ref}: distroless"
    return None, ""


files = dockerfiles()
if not files:
    fail("no Dockerfile was added")

codenames = {str(v.get("codename", "")).lower(): k for k, v in node_schedule().items() if v.get("codename")}
found = []
for path in files:
    text = path.read_text(encoding="utf-8", errors="replace")
    args = dict(ARG.findall(text))
    for raw in FROM.findall(text):
        ref = expand(raw, args)
        major, note = node_major(ref.lower(), codenames)
        if major is None and note:
            fail(f"{path.relative_to(WORKDIR)}: {note}")
        if major is not None:
            found.append((path.relative_to(WORKDIR), ref, major))

if not found:
    fail("no Node.js base image found in " + ", ".join(str(p.relative_to(WORKDIR)) for p in files))
bad = [(p, ref, major) for p, ref, major in found if not node_supported(major)]
if bad:
    fail("unsupported Node.js line(s): " + "; ".join(f"{p}: {ref} (Node {m})" for p, ref, m in bad))
ok("Node.js base image(s) on a supported LTS line: "
   + "; ".join(f"{p}: {ref} (Node {m})" for p, ref, m in found))
