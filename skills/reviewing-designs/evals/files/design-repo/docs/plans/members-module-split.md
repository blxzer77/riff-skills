# Plan: split app/ into modules

- `app/members/` — member records, owns the members table
- `app/loans/` — lending, reads members directly from the members table
- `app/shared/` — everything else that both need

Failure paths: if a member is deleted while they have a loan, loans keeps the row.
Rollback: revert the commit.
