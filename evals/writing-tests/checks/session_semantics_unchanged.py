#!/usr/bin/env python3
"""Sessions eval: fixing the flaky test must not change production expiry semantics.

The original store keeps a session valid at exactly ttl ms and expires it after.
"""

import os
import subprocess
import sys

PROBE = """
import { SessionStore } from "./src/session.js";
let t = 1000;
const realNow = Date.now;
Date.now = () => t;
const s = new SessionStore(50, () => t);
const id = s.create("u1");
t += 50;
const atTtl = s.get(id) !== null;
t += 1;
const after = s.get(id) === null;
Date.now = realNow;
console.log(JSON.stringify({ atTtl, after }));
"""
workdir = os.environ["EVAL_WORKDIR"]
path = os.path.join(workdir, "probe.mjs")
with open(path, "w") as f:
    f.write(PROBE)
try:
    r = subprocess.run(["node", "probe.mjs"], cwd=workdir, capture_output=True, text=True, timeout=60)
finally:
    os.unlink(path)
if r.returncode != 0:
    print(f"FAIL: probe crashed: {r.stderr[-600:]}")
    sys.exit(1)
res = __import__("json").loads(r.stdout)
if not res["atTtl"]:
    print("FAIL: sessions now expire at exactly the TTL; production semantics changed to fix a test")
    sys.exit(1)
if not res["after"]:
    print("FAIL: sessions no longer expire after the TTL")
    sys.exit(1)
print("PASS: expiry semantics unchanged (valid at ttl, expired after)")
