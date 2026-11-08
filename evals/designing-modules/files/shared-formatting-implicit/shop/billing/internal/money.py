def format_cents(cents: int, currency: str = "EUR") -> str:
    """Format an amount in minor units, e.g. 123456 -> 'EUR 1,234.56'."""
    sign = "-" if cents < 0 else ""
    whole, frac = divmod(abs(cents), 100)
    return f"{sign}{currency} {whole:,}.{frac:02d}"
