#!/usr/bin/env python3
"""Pass when helpdesk.triage, run against a fake client after a clean install, asks
for an active Claude model that is cheaper than the main model, and the tests pass.

The model is read from the request triage actually sends, so the check does not
depend on variable names or where the choice lives. "Active" and "cheaper" use
data/claude-model-status.json and data/claude-model-prices.json (official pages,
dated); an ID absent from them fails, since it was most likely recalled from memory.
"""

import json
import re
import textwrap

from tech_lib import DATA, WORKDIR, fail, install_and_run, ok

PROBE = textwrap.dedent("""
    import inspect, json, sys, types
    sys.path.insert(0, ".")
    calls = []

    class Messages:
        def create(self, **kwargs):
            calls.append(kwargs)
            return types.SimpleNamespace(content=[types.SimpleNamespace(type="text", text="billing")],
                                         stop_reason="end_turn")

    class Client:
        def __init__(self, *a, **k):
            self.messages = Messages()

    import anthropic
    anthropic.Anthropic = Client
    import helpdesk
    from helpdesk import sample_ticket, triage
    params = inspect.signature(triage).parameters
    kwargs = {"llm": Client()} if "llm" in params else {"client": Client()} if "client" in params else {}
    triage(sample_ticket(), **kwargs)
    assert calls, "triage did not call the model"
    print("MODEL=" + json.dumps(calls[-1].get("model")))
""")


def status(mid: str) -> str:
    models = json.loads((DATA / "claude-model-status.json").read_text(encoding="utf-8"))["models"]
    if mid in models:
        return models[mid]["status"]
    for full, info in models.items():
        if re.sub(r"-\d{8}$", "", full) == mid:
            return info["status"]
    return "unknown"


def input_price(mid: str) -> float | None:
    prices = json.loads((DATA / "claude-model-prices.json").read_text(encoding="utf-8"))["input_per_mtok"]
    if mid in prices:
        return prices[mid]
    alias = re.sub(r"-\d{8}$", "", mid)
    return prices.get(alias)


probe = WORKDIR / ".probe_triage_model.py"
probe.write_text(PROBE, encoding="utf-8")
try:
    passed, out = install_and_run(WORKDIR / "requirements.txt", [probe.name], ["-m", "unittest", "-q"])
    if not passed:
        lines = [l for l in out.strip().splitlines() if l.strip()]
        fail(lines[-1] if lines else out)
    passed, out = install_and_run(WORKDIR / "requirements.txt", [probe.name])
finally:
    probe.unlink(missing_ok=True)

m = re.search(r"^MODEL=(.*)$", out, re.M)
model = json.loads(m.group(1)) if m else None
if not isinstance(model, str):
    fail(f"could not read the model triage requests: {out[-300:]}")
model = re.sub(r"^(?:[\w.-]*?anthropic\.)", "", model)

state = status(model)
if state != "active":
    fail(f"triage uses {model} ({state} on the snapshot date)")
main_price = input_price("claude-sonnet-4-5-20250929")
price = input_price(model)
if price is None:
    fail(f"no published price for {model} in the snapshot")
if price >= main_price:
    fail(f"triage uses {model} at ${price}/MTok input, not cheaper than the main model (${main_price})")
ok(f"triage uses active model {model} at ${price}/MTok input (main model ${main_price}); tests pass")
