#!/usr/bin/env python3
"""Shop eval: percent + free-shipping coupons together must not charge shipping (hidden oracle)."""

import os
import subprocess
import sys

probe = r"""
from shop.pricing import Coupon, total
items = [{"sku": "poster", "price": 20.0, "qty": 1}]
both = [Coupon("SAVE10", "percent", 10), Coupon("FREESHIP", "free_shipping")]
assert total(items, both) == 18.0, total(items, both)
assert total(items, list(reversed(both))) == 18.0, total(items, list(reversed(both)))
assert total(items, [Coupon("SAVE10", "percent", 10)]) == 22.99
assert total([{"sku": "desk", "price": 60.0, "qty": 1}], [Coupon("SAVE10", "percent", 10)]) == 54.0
assert total([{"sku": "mug", "price": 12.0, "qty": 1}]) == 16.99
"""
r = subprocess.run([sys.executable, "-c", probe], cwd=os.environ["EVAL_WORKDIR"],
                   capture_output=True, text=True, timeout=60)
if r.returncode != 0:
    print("FAIL: pricing still wrong")
    print(r.stderr[-1000:])
    sys.exit(1)
print("PASS: combined coupons price correctly and existing behavior is unchanged")
