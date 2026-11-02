# Proposal: import monthly stock counts from a spreadsheet

Author: Mia · 2026-10-31

## Problem
Once a month two volunteers count the shelves and type the numbers into a
spreadsheet. Someone then edits each item by hand. We want to upload the
sheet as CSV instead.

## Goals
- Upload a CSV (`sku,counted`) on a new `/inventory/import` page, for
  logged-in volunteers only.
- Each item's quantity becomes the counted number, and the difference is
  recorded in `stock_moves` so the history still adds up.
- The whole file applies or none of it does.

## Non-goals
- Adding new items (unknown SKUs are reported and the import is refused).
- Partial imports.

## Design
The view (with `@login_required`) reads the file with the standard `csv`
module; the sheet is about 400 rows, so it runs inside the request.
It calls a new `apply_count(rows)` in `app/inventory/api.py`, which, in
one transaction:

1. Checks every SKU exists; if not, rolls back and returns the unknown SKUs.
2. For each row, inserts a `stock_moves` row with
   `kind = 'import'`, `quantity = counted - current`, `moved_at = now (UTC)`.
3. Sets `inventory_items.quantity = counted`.

Everything stays inside the inventory module (ADR 0002) and SQLite
(ADR 0001).

## Alternatives considered
- Editing items one by one: what we do now.
- A background job: unnecessary for 400 rows.

## Rollout and rollback
One deploy. Rollback is reverting the commit; imported moves stay in the
history, which is what we want.

## Tests
With a temporary database from `app/schema.sql`: a valid file sets the
quantities and writes one move per row; an unknown SKU changes nothing;
the moves for an item sum to its quantity.
