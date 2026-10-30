from dataclasses import dataclass

SHIPPING_FLAT = 4.99
FREE_SHIPPING_THRESHOLD = 50.00


@dataclass(frozen=True)
class Coupon:
    code: str
    kind: str  # "percent" or "free_shipping"
    value: float = 0.0


def subtotal(items):
    return round(sum(i["price"] * i["qty"] for i in items), 2)


def shipping(amount, coupons):
    if amount >= FREE_SHIPPING_THRESHOLD:
        return 0.0
    if any(c.kind == "free_shipping" for c in coupons):
        return 0.0
    return SHIPPING_FLAT


def total(items, coupons=()):
    amount = subtotal(items)
    for c in coupons:
        if c.kind == "percent":
            amount = round(amount * (1 - c.value / 100), 2)
            fee = SHIPPING_FLAT if amount < FREE_SHIPPING_THRESHOLD else 0.0
            return round(amount + fee, 2)
    return round(amount + shipping(amount, coupons), 2)
