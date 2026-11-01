from decimal import Decimal, ROUND_HALF_UP


def partial_refund(total: Decimal, percent: int) -> Decimal:
    return (total * percent / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
