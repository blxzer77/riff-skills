# Proposal: search box on the stock page

Author: Ken · 2026-10-31

## Problem
Volunteers packing boxes scroll the whole `/inventory` table (about 400
items) to find things like "oat milk". They want a search box.

## Goals
- Type part of a name or category, see matching in-stock items.
- Results in well under a second.
- No new service: two volunteers maintain this.

## Non-goals
- Typo tolerance, synonyms, ranking, accent folding, matching separate words.
- Searching donors or households.

## Design
Add an optional `q` argument to `items_in_stock(q=None)` in
`app/inventory/api.py`. When `q` is given, it adds
`AND (name LIKE ? ESCAPE '\' OR category LIKE ? ESCAPE '\')`, binding
`%` + q + `%` after escaping `\`, `%` and `_` in q with a backslash, so
typed wildcards match literally. The query stays inside the inventory
module (ADR 0002) and in SQLite (ADR 0001). A blank or whitespace-only
`q` means no filter. The whole text is matched as one phrase; matching
separate words is a non-goal for now. The `/inventory` view passes `request.args.get("q")` and the
template gets a GET form with one text field.

400 rows with a LIKE scan is a few milliseconds; we will not add an
index or SQLite FTS until the table is far larger.

## Alternatives considered
- SQLite FTS5: better matching, but a second table to keep in sync for
  400 rows.
- Filtering in the browser with JavaScript: the page would have to load
  all items anyway; fine today, but the LIKE version is as simple.
- Elasticsearch or Postgres full-text search: a new service to run.

## Rollout and rollback
One deploy. Rollback is reverting the commit.

## Tests
With a temporary database from `app/schema.sql`: `q="oat"` returns oat
milk and oats, not rice; `q` with `%` or `_` matches literally; `q=None`
returns everything in stock; out-of-stock items never appear.
