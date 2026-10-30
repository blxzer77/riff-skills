from datetime import date, timedelta

TERMS_DAYS = {"net15": 15, "net30": 30, "net60": 60}


def due_date(issued: date, terms: str) -> date:
    """Date an invoice is due, given its issue date and payment terms."""
    return issued + timedelta(days=TERMS_DAYS[terms])
