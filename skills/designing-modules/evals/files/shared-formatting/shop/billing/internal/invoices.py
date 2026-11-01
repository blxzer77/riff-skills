from shop.billing.internal.money import format_cents


def invoice_text(order_id: str, amount_cents: int) -> str:
    return f"Invoice for {order_id}: {format_cents(amount_cents)}"
