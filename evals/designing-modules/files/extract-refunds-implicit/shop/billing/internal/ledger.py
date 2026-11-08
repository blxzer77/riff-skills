LEDGER: list[tuple[str, int]] = []


def record_refund(order_id: str, amount_cents: int) -> None:
    LEDGER.append((order_id, -amount_cents))
