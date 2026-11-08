# Proposal: weekly donor impact report

Author: Mia · 2026-10-30

## Problem
The board wants a weekly CSV: for each donor, what they gave last week,
by item category and quantity. Today a volunteer builds it by hand.

## Goals
- `/backups/reports/donors-YYYY-MM-DD.csv` every Monday at 06:00.
- Runs in under a minute on current data (about 3,000 donations a year).

## Design
Add `app/reports/donor_report.py` with a `flask donor-report DEST`
command, registered in `app/cli.py` next to `backup`. It runs one SQL
query for the previous week:

    SELECT n.name, i.category, SUM(m.quantity)
    FROM donations d
    JOIN donors n ON n.id = d.donor_id
    JOIN stock_moves m ON m.donation_id = d.id
    JOIN inventory_items i ON i.sku = m.sku
    WHERE d.received_at >= ? AND d.received_at < ?
    GROUP BY n.name, i.category

and writes the rows to `DEST/donors-<date>.csv` with the standard
`csv` module, creating `DEST` if needed. One query keeps it fast and
easy to read.

Add a line to `deploy/crontab`, next to the nightly backup:

    0 6 * * 1 cd /srv/pantry && docker compose exec -T web flask donor-report /backups/reports

## Alternatives considered
- Keep building it by hand: what we do now.
- A BI tool: another service and account for one weekly file.

## Tests
A test seeds a temporary SQLite database with two donors and three
donations and checks the CSV rows.
