# 1. Use Express and PostgreSQL

- Status: accepted
- Date: 2026-02-10

## Context

We need an HTTP API for the recipes app. The team knows Node and SQL.

## Decision

We will build the API with Express 4 and store data in PostgreSQL 16.

## Consequences

- Good: familiar stack, large ecosystem.
- Bad: Express has no built-in structure; we must keep our own conventions.
