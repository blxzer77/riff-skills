# Proposal: email reminders for pickups

Author: Ana · 2026-10-29

## Problem
About one household in six misses its pickup slot. Most say they forgot.

## Goals
- Email each household with an address about 24 hours before its slot.
- Never send the same reminder twice in normal operation.
- No new service: two volunteers maintain this.

## Non-goals
- SMS, and households without an email address (front desk calls them).
- Custom email templates; the text below is fine for now.

## Design
Add `flask send-reminders [--dry-run]` in `app/households/reminders.py`,
registered in `app/cli.py` next to `backup`. Households own `pickups` and
`households` (ADR 0002), so this stays inside the households module.

It selects pickups whose `slot_start` (ISO 8601 UTC, written by
`pickups.book`) is between now and now + 24 hours, whose household has a
non-empty email, and whose `reminded_at` is NULL. For each, it sends

    Subject: Reminder: your Riverside pickup on <weekday> at <time> (America/Chicago)
    Reply to this email if you need a different slot.

through `app/mailer.py`, then sets `reminded_at` in its own short
transaction. Each pickup is handled in its own `try`/`except`, so one bad
address or SMTP error is logged and the run moves on to the next pickup.
The window bounds are written with the same `isoformat(timespec="seconds")`
UTC form `pickups.book` uses, so the string comparison is exact.
`--dry-run` prints what it would send and changes nothing.

Add a line to `deploy/crontab`, next to the nightly backup. `flock -n`
skips a run if the previous one is still going:

    5 * * * * cd /srv/pantry && flock -n /tmp/reminders.lock docker compose exec -T web flask send-reminders

Delivery is at-least-once: if the process dies, or the `reminded_at`
update fails, after a send succeeds, that household gets a second
reminder an hour later. We accept that; a duplicate reminder is harmless
and rare. A failed send leaves `reminded_at` NULL, is logged, and is
retried on the next run; once the slot has started it is no longer
selected, so a bad address stops being retried by itself. Failures show
up in the cron mail the VM already sends to the coordinators, like the
backup's. Replies go to pantry@riverside-foodbank.example, the mailbox
the front desk already reads.

## Alternatives considered
- A background thread in the web app: gunicorn runs four workers
  (`deploy/gunicorn.conf.py`), so each would send its own copy.
- Celery with Redis: a broker to run and back up for one hourly job.

## Rollout and rollback
Ship the command, run it once by hand with `--dry-run`, then add the cron
line. Rollback is deleting the cron line.

## Tests
`app/mailer.send` is replaced with a fake through `unittest.mock.patch`,
and `PANTRY_DB` points at a temporary file created from `app/schema.sql`. A pickup 23 hours out is
reminded once; running the command twice sends one email; a pickup 25
hours out and a household without email are skipped; a failed send
leaves `reminded_at` NULL; `--dry-run` sends nothing.
