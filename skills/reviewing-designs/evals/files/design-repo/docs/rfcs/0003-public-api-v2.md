# RFC 3: Rename `dueDate` to `due_on` in the public API

Status: Draft

## Motivation
Partner apps use snake_case; `dueDate` is the only camelCase field.

## Plan
1. Rename the field in `lend()` and the `/api/v1/loans` response.
2. Release.

## Migration
Partners update their clients after we release.
