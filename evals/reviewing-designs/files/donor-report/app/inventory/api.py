"""Public functions of the inventory module. Other modules call these."""

from ..db import connect


def items_in_stock() -> list[dict]:
    rows = connect().execute(
        "SELECT sku, name, category, quantity FROM inventory_items WHERE quantity > 0"
    ).fetchall()
    return [dict(r) for r in rows]


def received_between(start: str, end: str) -> list[dict]:
    """Stock received from donations in [start, end), one row per donation line."""
    rows = connect().execute(
        "SELECT m.donation_id, i.sku, i.name, i.category, m.quantity "
        "FROM stock_moves m JOIN inventory_items i ON i.sku = m.sku "
        "WHERE m.kind = 'donation' AND m.moved_at >= ? AND m.moved_at < ?",
        (start, end),
    ).fetchall()
    return [dict(r) for r in rows]
