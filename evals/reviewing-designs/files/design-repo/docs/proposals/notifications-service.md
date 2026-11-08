# Proposal: split notifications into its own service

Author: Mia · 2026-10-21

## Summary
Move reminder and overdue emails out of the Flask app into a separate Go service
with its own Postgres database, deployed on Kubernetes. Loans publishes events to
Kafka (see ADR 2); the service consumes them and sends mail.

## Data flow
1. `lend()` writes the loan to SQLite and publishes `loan.created`.
2. notifications-svc stores a copy of the loan and schedules reminders.
3. When a book is returned, loans publishes `loan.returned`.

## Rollout
Big-bang switch on a Saturday. No rollback plan; the old code is deleted in the
same release.

## Tests
Manual testing in staging.

## Security
The service reads the SMTP password from a ConfigMap.
