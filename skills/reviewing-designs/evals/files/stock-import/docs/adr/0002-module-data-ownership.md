# 2. Each module owns its tables

Status: Accepted (2025-09-18)

## Context
The inventory schema changes almost every week during the stock-tracking
pilot. Twice in August a change to `inventory_items` broke the donor
thank-you letters, which queried that table directly.

## Decision
Each module owns its tables: inventory owns `inventory_items` and
`stock_moves`; donors owns `donors` and `donations`; households owns
`households` and `pickups`. Other modules read another module's data only
through the functions in its `api.py`. No SQL against another module's tables.

## Consequences
Cross-module reads cost an extra function and sometimes an extra query.
Inventory can change its schema without breaking other modules.
