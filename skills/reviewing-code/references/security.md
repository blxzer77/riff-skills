# Security review of a change

Verified on 2026-11-01. Adapted from the security review designs in `sources.md`.

Look only at security implications the change adds. Existing concerns go in the
pre-existing section or nowhere.

## Before looking for vulnerabilities

Read how the project already handles the area the change touches: its validation,
escaping, authorization helpers, query builders, and secret handling. A new path
that bypasses an established safe pattern is the strongest signal; a new path that
uses it is usually fine.

## What to trace

For each changed entry point, trace untrusted data to the operation it reaches:

| Category | Sink to look for |
|---|---|
| Injection | SQL, NoSQL, shell, template, or code evaluation built from input |
| Path and file | file paths, archive extraction, uploads built from input |
| Request forgery | outbound requests whose host or protocol comes from input, including after redirects |
| Authentication and authorization | checks moved, skipped, ordered after the effect, or keyed on client-supplied identity |
| Deserialization | unsafe loaders on data from outside the process |
| Secrets and data exposure | credentials in code, secrets or personal data in logs, responses, or caches shared across users |
| Cryptography | weak algorithms, predictable randomness, disabled certificate checks |

## What a finding needs

- The attacker: who authors the input, and the line showing the code trusts them.
- The path: source, sink, and every guard between them, each at `file:line`.
- The gain: what the attacker gets that their position did not already allow.
- An exploit scenario in one or two sentences.
- The fix: the smallest change that closes the path.

Then apply `false-positives.md`. Only report findings you would expect a security
engineer to raise in this pull request with confidence; a short list of real issues
is worth more than a long list of possibilities.
