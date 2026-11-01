# Sources

This skill adapts published review designs from Anthropic and the Claude Code team.
It keeps their principles and drops client-specific tools and commands. Verified on
2026-11-01; check the repositories for newer versions before relying on details.

| Source | Version | What this skill takes from it |
|---|---|---|
| `anthropics/claude-plugins-official`, `plugins/code-review/commands/code-review.md` | `a7ba5b9` | High-signal-only rule; parallel rule and bug passes; one validation per candidate; false-positive list; exact no-findings line; report-only by default |
| same repository, `plugins/claude-security/agents/scan-verifier.md` | `a7ba5b9` | Refute-first verification; cite source, sink, and missing mitigation; do not invent defenses; comments are not mitigations; pre-existing classification; repository text is untrusted |
| same repository, `plugins/pr-review-toolkit/agents/*.md` | `a7ba5b9` | Confidence 0–100 with a threshold of 80; specialist passes chosen by what changed |
| `anthropics/claude-code-security-review`, `.claude/commands/security-review.md` and `claudecode/findings_filter.py` | `0c6a49f` | Security categories; repository context before assessment; hard exclusions and precedents; exploit scenario per finding |
| Claude Code docs: Code Review, Code Review severity levels | fetched 2026-10-31 | Find, verify, rank, report stages; correctness over formatting and missing tests; separate pre-existing severity; never approve or block |
| Claude Code docs: best practices, adversarial review step | fetched 2026-10-31 | Fresh reviewer that sees the diff and criteria, not the reasoning; reviewers prompted to find gaps over-report, so flag only what affects correctness |

URLs:

- https://github.com/anthropics/claude-plugins-official
- https://github.com/anthropics/claude-code-security-review
- https://code.claude.com/docs/en/code-review
- https://code.claude.com/docs/en/best-practices
