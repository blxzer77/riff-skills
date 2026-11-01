# audit-log-api

Pagination for the audit-log endpoint. The HTTP layer passes `page` exactly as the
client sends it; clients request page `0` for the first page.

`review.patch` is the pending change; `src/` and `tests/` have it applied. Run tests
with `python3 -m unittest`.

PR description: "Add `page_slice` so the handler can return one page of entries."
