#!/usr/bin/env python3
"""Pass when pricing.supported_currencies(client) returns the currency codes from
the rates service, using the httpx client it is given, and the tests pass."""

import textwrap

from tech_lib import WORKDIR, fail, install_and_run, ok

PROBE = textwrap.dedent("""
    import sys
    sys.path.insert(0, ".")
    import httpx
    import pricing

    seen = []

    def handler(request):
        seen.append(str(request.url))
        if request.url.path.endswith("/currencies"):
            return httpx.Response(200, json={"currencies": [{"code": "EUR"}, {"code": "USD"}, {"code": "JPY"}]})
        return httpx.Response(404)

    fn = getattr(pricing, "supported_currencies", None)
    if fn is None:
        from pricing import rates
        fn = rates.supported_currencies
    result = fn(httpx.Client(transport=httpx.MockTransport(handler)))
    assert seen, "the given client was not used"
    assert sorted(result) == ["EUR", "JPY", "USD"], f"unexpected result {result!r}"
    print("ok", seen[0])
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
