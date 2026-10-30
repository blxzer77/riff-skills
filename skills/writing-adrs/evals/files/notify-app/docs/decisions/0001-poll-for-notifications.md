# 0001. Poll for dashboard notifications

- Status: accepted
- Date: 2026-01-12

## Context

The dashboard needs new build notifications. We have few users (under 50) and want
the simplest thing that works with our serverless hosting.

## Decision

We will poll `GET /api/notifications?since=<ts>` every 5 seconds from the browser.

## Consequences

- Good: no long-lived connections; works on any host.
- Bad: up to 5 s delay; constant request load even when idle.
