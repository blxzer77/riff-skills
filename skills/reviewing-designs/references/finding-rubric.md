# Finding rubric

## Confidence

- 0–49: plausible concern or preference; do not report.
- 50–79: needs evidence or a question; put in Missing evidence if useful.
- 80–89: concrete risk supported by the proposal/project; report as Important.
- 90–100: direct, reproducible failure or explicit violated constraint; report as High.

## Severity

- **High**: data loss, security exposure, incompatible public contract, unrecoverable
  migration, or a design that cannot meet a must-have.
- **Important**: likely user-facing failure, substantial coupling, missing rollback,
  or a quality attribute failure under a stated workload.
- **Suggestion**: low-risk improvement; do not mix it with blockers.

An issue is not a finding merely because another design is prettier. If evidence is
uncertain, ask a question or suppress it.
