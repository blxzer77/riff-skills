# API evolution

Use additive changes as the default: new fields, endpoints, states, or error metadata should not alter existing meaning. Treat requiredness, types, enum closure, authorization, ordering, pagination tokens, error codes, and side effects as compatibility surface. Verify with old-client fixtures or contract tests, not just schema validity.

For a breaking need, prefer a migration path: introduce the replacement, dual-read or dual-write where data requires it, instrument old usage, communicate a dated compatibility window, and remove only after usage and downstream owners are known. Version only the boundary that must diverge; do not create parallel versions preemptively. A deprecation record should name the replacement, affected callers, behavior differences, migration steps, notice date, removal condition, and owner.

Primary sources: RFC 9110 (HTTP Semantics), https://www.rfc-editor.org/rfc/rfc9110; RFC 8594 (Sunset HTTP Header Field), https://www.rfc-editor.org/rfc/rfc8594; RFC 9457 (Problem Details for HTTP APIs), https://www.rfc-editor.org/rfc/rfc9457. Verified on 2026-10-30.
