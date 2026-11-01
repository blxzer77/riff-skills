# 1. Use SQLite for storage

Status: Accepted (2025-04-02)

## Context
One VM, a few hundred members, two volunteer maintainers.

## Decision
Store everything in one SQLite file, backed up nightly with `sqlite3 .backup`.

## Consequences
Single writer; fine at this size. Revisit if we ever run more than one app process.
