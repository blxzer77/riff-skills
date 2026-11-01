# 4. In-process event bus between api and worker

Date: 2025-09-01 · Status: Accepted

## Context
The worker needs to react to new reviews. We run one api and one worker process.

## Decision
Use a Postgres LISTEN/NOTIFY channel as the event bus.

## Consequences
No new infrastructure. Events are lost if the worker is down when they fire.
