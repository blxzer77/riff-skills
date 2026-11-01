# profile-gateway

Serves user profiles over HTTP. Profiles contain private contact details. The cache is
shared by every request handled by the process.

`review.patch` is the pending change; the files under `src/` and `tests/` are the
tree with the change applied. Run tests with `python3 -m unittest`.

PR description: "Move the cache lookup earlier so cached profiles skip the auth
call, and simplify the cache key. Also normalize quotes."
