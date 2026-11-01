#!/usr/bin/env python3
"""Extract-refunds eval: refund logic now lives in a `shop.refunds` module and is no
longer implemented inside orders, and refunds still behave the same."""

import importlib
import sys

from module_lib import PACKAGE, WORKDIR

if not (PACKAGE / "refunds").is_dir() and not (PACKAGE / "refunds.py").is_file():
    print("FAIL: no shop.refunds module was created")
    sys.exit(1)

leftover = PACKAGE / "orders" / "internal" / "refunds.py"
if leftover.exists() and "def refund_order" in leftover.read_text(encoding="utf-8"):
    print("FAIL: refund_order is still implemented in shop/orders/internal/refunds.py")
    sys.exit(1)

sys.path.insert(0, str(WORKDIR))
try:
    orders = importlib.import_module("shop.orders")
    refunds = importlib.import_module("shop.refunds")
except Exception as exc:  # noqa: BLE001
    print(f"FAIL: could not import shop.orders / shop.refunds: {exc!r}")
    sys.exit(1)

entry = getattr(refunds, "refund_order", None)
if entry is None:
    print("FAIL: shop.refunds does not expose refund_order in its public API")
    sys.exit(1)

orders.place_order("Z1", 1000)
try:
    first, second = entry("Z1", 400), entry("Z1", 100)
except Exception as exc:  # noqa: BLE001
    print(f"FAIL: shop.refunds.refund_order raised {exc!r}")
    sys.exit(1)
if (first, second) != (400, 500):
    print(f"FAIL: refunds no longer accumulate correctly: {(first, second)}")
    sys.exit(1)
try:
    entry("Z1", 600)
except ValueError:
    pass
else:
    print("FAIL: a refund above the order total was accepted")
    sys.exit(1)
print("PASS: shop.refunds owns refund_order and behavior is preserved")
