# Authorization and cache review fixture

`review.patch` is the proposed change. The files under `src/` and `tests/` are the
post-change tree. The endpoint returns private profiles and the existing contract
requires an unauthorized request to receive 403 before profile data is read or
returned. The supplied test covers only the owner path.
