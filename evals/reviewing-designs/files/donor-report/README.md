# pantry

Inventory and pickup scheduling for the Riverside community food bank.
Flask on gunicorn, SQLite. Two volunteer maintainers; deployed on one VM with
`deploy/compose.yml`. Times are stored in UTC and shown in America/Chicago.
Run tests with `python3 -m unittest`.

- `app/inventory/` — items and stock
- `app/donors/` — donors and donations
- `app/households/` — registered households and their pickups
- `app/api/v1/` — JSON API
- `docs/adr/` — accepted decisions
- `docs/proposals/`, `docs/plans/` — designs under discussion
