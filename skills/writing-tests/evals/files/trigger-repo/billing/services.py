def apply_credit(account, amount_cents: int) -> int:
    if amount_cents <= 0:
        raise ValueError("credit must be positive")
    account.balance -= amount_cents
    account.save()
    return account.balance
