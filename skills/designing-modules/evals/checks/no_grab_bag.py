#!/usr/bin/env python3
"""Pass when no new shared grab-bag module (utils, common, shared, helpers, ...) was
added under shop/, and the order confirmation now shows the formatted total."""

import importlib
import sys

from module_lib import WORKDIR, grab_bag_modules

bags = grab_bag_modules()
if bags:
    print(f"FAIL: shared grab-bag module added: {bags}")
    sys.exit(1)

sys.path.insert(0, str(WORKDIR))
try:
    orders = importlib.import_module("shop.orders")
    text = orders.confirmation_text("X9", 2, 123456)
except Exception as exc:  # noqa: BLE001
    print(f"FAIL: shop.orders.confirmation_text failed: {exc!r}")
    sys.exit(1)
if "1,234.56" not in text:
    print(f"FAIL: confirmation does not show the formatted total: {text!r}")
    sys.exit(1)
print("PASS: no grab-bag module; confirmation shows the formatted total")
