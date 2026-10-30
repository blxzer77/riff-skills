# Async and realtime contracts

For long-running work, return a durable operation identity and define states, result retrieval, failure details, cancellation, expiry, authorization, and retry behavior. A client must be able to reconnect and inspect status without relying on the original request. Use polling when updates are infrequent and no push channel is needed.

Use SSE for server-to-client ordered updates with reconnect support; define event names, IDs, retry guidance, heartbeats, authorization renewal, and a last-seen resumption strategy. Use webhooks when the receiver is disconnected or delivery must cross a system boundary; sign messages, include event IDs and schema versions, retry with bounded backoff, and document deduplication and replay/reconciliation. Assume at-least-once delivery unless tests prove otherwise.

Primary sources: WHATWG HTML, Server-sent events, https://html.spec.whatwg.org/multipage/server-sent-events.html; RFC 9110 (HTTP Semantics), https://www.rfc-editor.org/rfc/rfc9110; CloudEvents specification, https://github.com/cloudevents/spec. Verified on 2026-10-30.
