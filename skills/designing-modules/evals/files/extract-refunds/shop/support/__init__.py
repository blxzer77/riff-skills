"""Support desk actions."""

from shop import billing
from shop.orders import refund_order


def issue_goodwill_refund(order_id: str, amount_cents: int) -> int:
    total = refund_order(order_id, amount_cents)
    billing.record_refund(order_id, amount_cents)
    return total
