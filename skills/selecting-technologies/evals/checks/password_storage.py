#!/usr/bin/env python3
"""Pass when, after a clean install of requirements.txt, passwords are stored with a
salted slow hash that still verifies, and the project's tests pass.

Salted: two accounts with the same password get different stored values. Slow: the
median signup takes at least MIN_MS. A salted SHA-256 takes microseconds; bcrypt,
scrypt, Argon2id, or PBKDF2 at OWASP minimum parameters take tens of milliseconds,
so the threshold separates them with a wide margin. Load only slows hashing, so it
cannot turn a fast hash into a pass.
"""

import textwrap

from tech_lib import WORKDIR, fail, install_and_run, ok

PROBE = textwrap.dedent("""
    import hashlib, statistics, sys, time
    sys.path.insert(0, ".")
    from members import Accounts

    MIN_MS = 5
    accounts = Accounts()
    timings = []
    for i, email in enumerate(["a@example.com", "b@example.com", "c@example.com"]):
        start = time.perf_counter()
        accounts.signup(email, "correct horse")
        timings.append((time.perf_counter() - start) * 1000)
    median = statistics.median(timings)
    assert median >= MIN_MS, f"fast hash: median signup {median:.3f} ms < {MIN_MS} ms"

    def stored(email):
        if hasattr(accounts, "stored_hash"):
            return accounts.stored_hash(email)
        return accounts._users[email]

    a, b = stored("a@example.com"), stored("b@example.com")
    text = a.decode() if isinstance(a, bytes) else str(a)
    assert text != hashlib.sha256(b"correct horse").hexdigest(), "still plain SHA-256"
    assert a != b, "same password produced the same stored value (no salt)"
    assert accounts.login("a@example.com", "correct horse"), "right password rejected"
    assert not accounts.login("a@example.com", "wrong horse"), "wrong password accepted"
    print(f"median signup {median:.1f} ms; stored: {text[:30]}")
""")

probe = WORKDIR / ".probe_password_storage.py"
probe.write_text(PROBE, encoding="utf-8")
try:
    passed, out = install_and_run(WORKDIR / "requirements.txt", [probe.name], ["-m", "unittest", "-q"])
finally:
    probe.unlink(missing_ok=True)
if not passed:
    lines = [l for l in out.strip().splitlines() if l.strip()]
    fail("after a clean install of requirements.txt: " + (lines[-1] if lines else out))
ok("salted slow hash that verifies, and tests pass, after a clean install")
