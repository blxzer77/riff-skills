def confirmation_text(order_id: str, item_count: int, total_cents: int) -> str:
    return f"Order {order_id} confirmed: {item_count} item(s)."
