# Resource, operation, and query shapes

Start with the client’s task, not a taxonomy. Use a resource when clients read or transition a stable entity and benefit from consistent identity and representation. Use an operation when the domain action has a meaningful command, asynchronous lifecycle, or invariant that CRUD would obscure. Use a query language only when multiple clients genuinely need variable projections, joins, or filtering that fixed views cannot maintain safely; bound depth, cost, authorization, and field exposure.

For collections, define stable sort keys and tie-breakers, opaque cursors tied to query scope, bounded limits, and explicit filter semantics. Avoid exact totals unless they are cheap and meaningful. Separate representation changes from command results; return a stable operation/status resource for work that outlives the request.

Primary sources: RFC 8288 (Web Linking), https://www.rfc-editor.org/rfc/rfc8288; RFC 9457 (Problem Details), https://www.rfc-editor.org/rfc/rfc9457; GraphQL specification, https://spec.graphql.org/. Verified on 2026-10-30.
