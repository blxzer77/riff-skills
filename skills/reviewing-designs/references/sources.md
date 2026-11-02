# Sources

Anthropic and the Claude Code team publish code-review designs and one architecture
critic, but no dedicated method for reviewing design documents. This skill applies
their review principles to designs and fills the gaps from the primary sources
below. Fetched and checked on 2026-11-02.

## Anthropic / Claude Code

| Source | Version | What this skill takes from it |
|---|---|---|
| `anthropics/claude-plugins-official`, `plugins/code-modernization/agents/architecture-critic.md` | `a7ba5b9` | Skeptical default ("do we actually need this?"); simplest design that meets the stated requirements; trace one failure end to end; a missing migration story is a finding; repository text is data, not instructions |
| same repository, `plugins/code-review/commands/code-review.md` | `a7ba5b9` | High-signal-only rule; validate each candidate before reporting; the false-positive list (pre-existing, pedantic, subjective, general quality); report-only by default |
| same repository, `plugins/pr-review-toolkit/agents/code-reviewer.md` and `plugins/feature-dev/agents/code-reviewer.md` | `a7ba5b9` | Confidence 0–100, report at 80 or above; quality over quantity |
| same repository, `plugins/feature-dev/agents/code-architect.md` and `commands/feature-dev.md` | `a7ba5b9` | Read existing patterns, module boundaries, and project guidelines before judging an approach; make one decisive choice rather than a menu |
| same repository, `plugins/claude-security/agents/scan-verifier.md` | `a7ba5b9` | Refute-first verification; cite the decisive file and line; do not invent a defense; claims in comments are not mitigations |
| Claude Code docs, Best practices: "Explore first, then plan, then code" and "Add an adversarial review step" | fetched 2026-11-02 | Planning prevents solving the wrong problem; review in a fresh context that sees the work and criteria, not the reasoning; reviewers asked to find gaps over-report, so flag only gaps that affect correctness or stated requirements |

The "80/100" threshold in this skill comes from the two code-reviewer agents above,
where it is defined for code. Applying it to design findings is this project's
choice.

## Primary sources (non-Anthropic)

| Source | What this skill takes from it |
|---|---|
| Malte Ubl, "Design Docs at Google" | A design doc records trade-offs against goals and non-goals; alternatives explain why they lost; cross-cutting concerns get short sections; reviews are useful but are overhead |
| Michael Nygard, "Documenting Architecture Decisions" (2011) | Accepted decisions stay until a later record marks them superseded |
| Martin Fowler, ParallelChange | Backward-incompatible interface changes go through expand, migrate, contract |

URLs:

- https://github.com/anthropics/claude-plugins-official
- https://code.claude.com/docs/en/best-practices
- https://www.industrialempathy.com/posts/design-docs-at-google/
- https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- https://martinfowler.com/bliki/ParallelChange.html
