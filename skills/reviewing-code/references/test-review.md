# Test review

Verified on 2026-10-30.

Judge tests by behavioral risk, not line coverage. For each changed behavior, identify the public or integration contract, normal case, boundary/invalid case, failure or recovery case, and compatibility-sensitive case. Prefer assertions on externally observable results, persisted state, emitted events, authorization outcomes, and meaningful errors over implementation details.

Weight coverage by criticality:

- Critical paths (money, permissions, data loss, migrations, destructive operations, privacy, availability): require focused tests for success and the highest-impact failure/boundary behavior; favor an integration or end-to-end seam where unit isolation could miss wiring.
- Important paths (user-visible workflows and core business rules): cover normal behavior plus changed boundaries and representative failures.
- Low-risk paths (formatting, adapters, localized refactors): a focused unit test or existing contract may be sufficient.

A missing test is reportable only when the change introduces a plausible regression and the absence of a behavioral check makes it easy to ship. Do not demand tests for unchanged behavior, generated code, trivial delegation, or every branch mechanically. Test flakiness, order dependence, broad mocks, assertions that can pass on the wrong result, and tests that never exercise the changed path are themselves review evidence when introduced by the change.

When tests cannot run, inspect their path and assertions, state that limitation, and do not claim execution. Separate “tests pass” from “tests are adequate.”
