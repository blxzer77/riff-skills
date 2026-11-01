#!/usr/bin/env python3
"""Pass when every dependency added to requirements.txt is still released.

A package whose last release (on or before the snapshot date) is more than
MAX_AGE_DAYS old fails: it is not receiving fixes. Adding no dependency passes;
standard-library solutions are judged by the behavior check, not here.
"""

from datetime import date

from tech_lib import AS_OF, added_requirements, fail, last_release, ok

MAX_AGE_DAYS = 3 * 365

added = added_requirements()
if not added:
    ok("no dependency added to requirements.txt")

stale, unknown, fresh = [], [], []
for name in sorted(added):
    released = last_release(name)
    if released is None:
        unknown.append(name)
        continue
    age = (AS_OF - date.fromisoformat(released)).days
    (stale if age > MAX_AGE_DAYS else fresh).append(f"{name} (last release {released})")

if unknown:
    fail(f"could not find on PyPI: {unknown}")
if stale:
    fail(f"added dependency not released in over {MAX_AGE_DAYS // 365} years: {stale}")
ok(f"added dependencies are maintained: {fresh}")
