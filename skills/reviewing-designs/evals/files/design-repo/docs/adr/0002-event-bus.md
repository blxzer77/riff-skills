# 2. Introduce an event bus between loans and notifications

Status: Proposed (2026-10-20)

## Context
When a loan is created we want to email the member. Later we may add SMS and a
digest.

## Decision
Run Kafka (three brokers) and publish `loan.created` events. A new notifications
service consumes them.

## Consequences
Loans and notifications are decoupled and can scale independently.
