# Security review fixture

`review.patch` is the proposed change and `src/` is the post-change tree. The
callback payload is attacker-influenced and is accepted only after host allowlisting.
Production passes `ProductionHttpClient` from `src/http_client.py`; it uses requests,
accepts the raw URL, and follows redirects. The test uses a fake boundary and is not
production code. Review whether each issue is reachable and actionable rather than
treating a test-only input as an exploit by itself.
