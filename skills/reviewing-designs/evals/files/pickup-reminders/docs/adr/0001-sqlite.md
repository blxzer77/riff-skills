# 1. Use SQLite for all application data

Status: Accepted (2025-03-02)

## Context
One VM, about 600 registered households, two volunteer maintainers, no ops staff.

## Decision
Keep all application data in one SQLite file on the `pantry-data` volume,
backed up nightly by `flask backup` (see `deploy/crontab`).

## Consequences
One writer at a time; fine at this size. No second database to run or back up.
Revisit if we need more than one VM.
