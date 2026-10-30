# Security review

Verified on 2026-10-30.

Start with assets and trust boundaries: identify the actor, input source, privilege, sensitive asset, and intended authorization decision. Trace data to its sink and check validation, canonicalization, encoding, secret handling, access control, tenant isolation, replay/idempotency, resource limits, logging, and dependency/configuration changes.

Report a security finding only when the patch creates or worsens a reachable path with a concrete attacker capability, violated security property, and plausible impact. Look for exploitability in the deployed context, not just an API name or a missing defense-in-depth layer. Suppress false positives when a trusted boundary is enforced elsewhere and verify that claim in code/configuration. Do not report test fixtures, unreachable branches, theoretical attacks requiring an already-compromised privilege, or generic hardening advice as defects.

For each candidate, document: attacker capability; entry point; relevant asset; missing or bypassed control; exploit sequence; impact; and why existing controls do not stop it. Consider both direct and indirect effects such as information disclosure through errors, authorization checks after mutation, unsafe redirects, command/query/template injection, path confusion, unbounded work, and secrets in logs.

Security severity follows realistic impact and reachability. Avoid exact scoring systems unless the project supplies one; use the review severity labels and confidence threshold in the parent skill.
