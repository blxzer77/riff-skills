#!/usr/bin/env python3
"""Pass when pricing.supported_currencies(client) requests the currencies URL with the
httpx client it is given and returns the codes, and the tests pass.

The prompt does not specify the response body, so the probe serves several plausible
shapes and passes if the function returns the codes for any one of them.
"""

import textwrap

from tech_lib import WORKDIR, fail, install_and_run, ok

PROBE = textwrap.dedent("""
    import sys
    sys.path.insert(0, ".")
    import httpx
    import pricing

    CODES = ["EUR", "JPY", "USD"]
    SHAPES = [
        {"currencies": CODES},
        {"currencies": [{"code": c} for c in CODES]},
        {"currencies": {c: c for c in CODES}},
        CODES,
        [{"code": c} for c in CODES],
        {"data": CODES},
        {"codes": CODES},
    ]

    fn = getattr(pricing, "supported_currencies", None)
    if fn is None:
        from pricing import rates
        fn = rates.supported_currencies

    tried = []
    for body in SHAPES:
        seen = []

        def handler(request, body=body):
            seen.append(request.url)
            if request.url.path.endswith("/currencies"):
                return httpx.Response(200, json=body)
            return httpx.Response(404)

        try:
            result = fn(httpx.Client(transport=httpx.MockTransport(handler)))
        except Exception as exc:
            tried.append(f"{type(exc).__name__}")
            continue
        if not seen:
            raise SystemExit("the given client was not used")
        try:
            if sorted(str(c) for c in result) == CODES:
                print("ok", seen[0], "shape", type(body).__name__)
                raise SystemExit(0)
        except TypeError:
            pass
        tried.append(repr(result)[:60])
    raise SystemExit(f"no plausible response shape returned the codes: {tried}")
""")

probe = WORKDIR / ".probe_currencies.py"
probe.write_text(PROBE, encoding="utf-8")
try:
    passed, out = install_and_run(WORKDIR / "requirements.txt", [probe.name], ["-m", "unittest", "-q"])
finally:
    probe.unlink(missing_ok=True)
if not passed:
    lines = [l for l in out.strip().splitlines() if l.strip()]
    fail(lines[-1] if lines else out)
ok("supported_currencies works with the given httpx client and tests pass")
