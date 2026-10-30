# Finding rubric

Verified on 2026-10-30.

A reportable finding satisfies all four gates:

1. **Introduced:** the proposed change causes or materially worsens it; a pre-existing defect is suppressed.
2. **Reachable:** a supported caller, input, deployment, or failure condition can trigger it.
3. **Impactful:** it violates a contract or creates a concrete correctness, reliability, security, or data-integrity consequence.
4. **Actionable:** the author can locate and fix it from the file, line, evidence, and remediation.

Confidence is the reviewer’s probability that all four gates hold. Report only confidence of at least 80%. A suspicious pattern is not evidence. If an assumption is necessary, state it and lower confidence; ask the requester when the assumption changes the result.

Severity is about consequence, not ease of fixing:

- **blocker:** severe security, data loss/corruption, or release-stopping breakage in a realistic supported path.
- **major:** likely production failure, broken compatibility/contract, or material security/reliability impact.
- **minor:** real, bounded defect with limited impact or a less critical path.

Do not report formatting, naming preference, refactoring taste, existing linter warnings, pedantic concerns, or a theoretical future problem. A test gap is a finding only when the missing behavioral assertion leaves a meaningful changed risk unguarded; explain the risk rather than requesting tests by habit.
