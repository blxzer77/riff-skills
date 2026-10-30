# Review pass matrix

Verified on 2026-10-30. Use only for a scoped change review.

| Pass | Questions | Evidence to seek |
|---|---|---|
| Scope and intent | What behavior is intended, and what is actually changed? | merge-base, diff, issue/requirements, callers |
| Correctness | Can valid and invalid inputs cross every branch safely? Are invariants and compatibility preserved? | control flow, state transitions, boundaries, sibling code |
| Failure behavior | What happens on timeout, retry, cancellation, partial write, stale data, or dependency failure? | error paths, cleanup, logging, idempotency |
| Test adequacy | Do tests assert observable behavior for critical paths and changed boundaries? | tests, fixtures, failure assertions, integration seams |
| Security | Can an untrusted actor cross a trust boundary or affect an asset? | authn/authz, validation, encoding, secrets, resource limits |
| Maintainability | Is there a smaller or clearer implementation that avoids a defect? | duplication, abstractions, dead branches, history |

Parallel passes are useful when each pass has a narrow question and receives the same scope. Reconcile duplicate candidates centrally, preserve the strongest evidence, then validate each candidate against the base. Sequential passes are preferable when later passes depend on discovered data flow or when context isolation is unavailable.

Do not turn this matrix into a repository-wide checklist. Stop once the scoped paths and their likely consequences have been covered.

## Reconciliation

For each candidate, record: changed line, affected path, pre-change behavior, post-change behavior, trigger, impact, evidence, confidence, and whether the base already had it. Discard duplicates, pre-existing issues, tool-only noise, and candidates lacking a realistic trigger.

## Primary sources

These sources informed the workflow; verify time-sensitive guidance before reuse. Verified on 2026-10-30.

- Anthropic, “Claude Code best practices”: https://www.anthropic.com/engineering/claude-code-best-practices
- Google Engineering Practices, “Code review developer guide”: https://google.github.io/eng-practices/review/
- Google Engineering Practices, “How to do a code review”: https://google.github.io/eng-practices/review/reviewer/
