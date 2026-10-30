## API design guardrail

When changing an API, inspect existing routes, schemas, clients, tests, and project conventions first. Choose the smallest contract that meets the actual client query and failure needs; do not add HATEOAS, federation, gateways, or extra versions without evidence. Specify stable identifiers, error codes, pagination and ordering, retry/idempotency behavior, async lifecycle, and compatibility impact. Validate old-client behavior and malformed, unauthorized, duplicate, stale, and partial-failure cases before calling the change safe.
