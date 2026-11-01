from dataclasses import dataclass

from shop import billing

_ORDERS: dict[str, "Order"] = {}


@dataclass
class Order:
    order_id: str
    total_cents: int
    paid: bool = False


def place_order(order_id: str, total_cents: int) -> Order:
    order = Order(order_id, total_cents)
    _ORDERS[order_id] = order
    billing.open_invoice(order_id, total_cents)
    return order


def get_order(order_id: str) -> Order:
    return _ORDERS[order_id]


def mark_paid(order_id: str) -> None:
    _ORDERS[order_id].paid = True
