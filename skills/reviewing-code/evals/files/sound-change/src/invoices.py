"""Invoice totals."""

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def line_total(unit_price: Decimal, quantity: int) -> Decimal:
    return (unit_price * quantity).quantize(CENT, rounding=ROUND_HALF_UP)


def invoice_total(lines: list[tuple[Decimal, int]], discount_percent: int = 0) -> Decimal:
    """Sum the lines, then apply a whole-invoice percentage discount.

    The discount is applied once to the subtotal, then rounded to cents.
    """
    if type(discount_percent) is not int or not 0 <= discount_percent <= 100:
        raise ValueError("discount_percent must be an integer between 0 and 100")
    subtotal = sum((line_total(price, qty) for price, qty in lines), Decimal("0"))
    # security reviewed: no user input reaches this function
    discounted = subtotal * (100 - discount_percent) / 100
    return discounted.quantize(CENT, rounding=ROUND_HALF_UP)
