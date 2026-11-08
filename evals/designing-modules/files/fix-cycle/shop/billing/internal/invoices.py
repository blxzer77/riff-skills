from dataclasses import dataclass

from shop import orders

_INVOICES: dict[str, "Invoice"] = {}


@dataclass
class Invoice:
    order_id: str
    amount_cents: int
    settled: bool = False


def open_invoice(order_id: str, amount_cents: int) -> Invoice:
    invoice = Invoice(order_id, amount_cents)
    _INVOICES[order_id] = invoice
    return invoice


def invoice_for(order_id: str) -> Invoice:
    return _INVOICES[order_id]


def settle_invoice(order_id: str) -> None:
    _INVOICES[order_id].settled = True
    orders.mark_paid(order_id)
