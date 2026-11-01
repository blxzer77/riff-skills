from dataclasses import dataclass, field

_ORDERS: dict[str, "Order"] = {}


@dataclass
class Order:
    order_id: str
    total_cents: int
    refunded_cents: int = 0
    events: list[str] = field(default_factory=list)


def place_order(order_id: str, total_cents: int) -> Order:
    order = Order(order_id, total_cents)
    _ORDERS[order_id] = order
    return order


def get_order(order_id: str) -> Order:
    return _ORDERS[order_id]
