## Design review

Before implementing a non-trivial architecture or API change, review the proposal
against the actual repository. It should state goals, non-goals, alternatives, tradeoffs,
module/data boundaries, failure and rollback behavior, tests, and a revisit trigger.
Prefer the smallest design that meets proven requirements; record costly-to-reverse
choices in an ADR. High-confidence review findings include location, impact, evidence,
and the smallest fix.
