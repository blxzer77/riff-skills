# Incremental migration

Use this reference when a boundary must change without a risky rewrite.

## Branch by abstraction

For an internal replacement, introduce a narrow abstraction at the existing call site, implement the old path behind it, add contract tests, then add the new path and switch callers incrementally. Measure both paths where behavior or performance can differ. Remove the old implementation and the temporary abstraction after a stable period; otherwise the seam becomes permanent debt.

## Strangler path

For an extracted capability, put a routing seam in front of the old implementation, establish the new capability's contract and data ownership, route a small safe slice, compare outcomes, expand gradually, and retire the old path. Avoid simultaneous writes unless reconciliation and rollback are explicit. Prefer one owner for each invariant; temporary duplication needs a time limit and monitoring.

Every migration plan names: compatibility contract, traffic/data transition, observability, rollout gates, rollback action, owner, and deletion date. A migration that cannot roll back safely should be staged until it can.

## Sources

- Martin Fowler, “Strangler Fig Application,” martinfowler.com (primary essay), verified 2026-10-30: https://martinfowler.com/bliki/StranglerFigApplication.html
- Martin Fowler, “Branch by Abstraction,” martinfowler.com (primary essay), verified 2026-10-30: https://martinfowler.com/bliki/BranchByAbstraction.html
- Sam Newman, *Monolith to Microservices*, O'Reilly, 2019 (incremental extraction), verified 2026-10-30.
