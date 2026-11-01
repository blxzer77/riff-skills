#!/usr/bin/env bash
# Leaves a feature branch with commits ahead of main and one staged change, so any
# review request ("my branch", "staged changes", "this diff", "the last commits")
# has a real change to look at. Removed from the sandbox before the agent runs.
set -euo pipefail

git checkout -q -b feature/refunds

cat > billing/refund.py <<'PY'
from decimal import Decimal, ROUND_HALF_UP


def partial_refund(total: Decimal, percent: int) -> Decimal:
    return (total * percent / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def refund_shipping(order, amount: Decimal) -> Decimal:
    if amount > order.shipping:
        amount = order.shipping
    order.refunded += amount
    return amount
PY
git add billing/refund.py
git commit -q -m "Add shipping refunds"

cat > src/auth/middleware.ts <<'TS'
export function requireRole(user: { roles: string[] } | null, role: string): boolean {
  if (!user) return true;
  return user.roles.includes(role) || user.roles.includes("admin");
}
TS
git add src/auth/middleware.ts
git commit -q -m "Let admins through role checks"

cat > reports/builder.py <<'PY'
def monthly_report(db, month: str, sort: str = "created_at"):
    return db.execute(f"SELECT * FROM orders WHERE month = ? ORDER BY {sort}", (month,)).fetchall()
PY
git add reports/builder.py
