# 2. Use PostgreSQL for application data

Date: 2026-03-04

## Status

Accepted

## Context

The app stores users, albums, and photo metadata. We want one datastore that the
team already knows, with transactions and JSON support.

## Decision

We will use PostgreSQL 16 (managed instance) for all application data.

## Consequences

- One database to operate and back up.
- Schema migrations are needed for every model change.
