from shop.orders.internal.store import get_order


def refund_order(order_id: str, amount_cents: int) -> int:
    """Refund part of an order. Returns the total refunded so far."""
    order = get_order(order_id)
    if amount_cents <= 0:
        raise ValueError("refund amount must be positive")
    if order.refunded_cents + amount_cents > order.total_cents:
        raise ValueError("refund exceeds order total")
    order.refunded_cents += amount_cents
    order.events.append(f"refunded {amount_cents}")
    return order.refunded_cents
