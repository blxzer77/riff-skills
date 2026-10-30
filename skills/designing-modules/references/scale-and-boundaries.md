# Scale and boundaries

Use this reference when the team is choosing between a single module, a modular monolith, and services. The scale ladder is a decision aid, not a maturity model.

## Ladder

1. **Single module:** one deployable unit with explicit internal seams. Choose it when the system is small, the team shares ownership, and operational isolation is not a requirement.
2. **Modular monolith:** one deployable unit with modules that own capabilities and expose contracts. Choose it when change coupling and ownership clarity matter but independent deployment or failure isolation does not.
3. **Services:** separately deployable capabilities with explicit data and operational ownership. Choose only when independent scaling, release cadence, fault isolation, compliance, or team ownership pays for distributed-systems cost.

Promote a rung only when a lower rung cannot satisfy a named constraint. A modular monolith is often the best intermediate state because it tests boundaries without adding network, deployment, and data-consistency costs.

## Boundary test

A candidate boundary is credible when a representative capability change can be made mostly inside it, its invariant data is owned by it, collaborators use a small contract, and failures/ownership are understandable. If several changes routinely require synchronized edits in both sides, merge the boundary or redesign the contract before extracting it.

## Sources

- Martin Fowler, “MonolithFirst” and “Microservice Premium,” martinfowler.com (primary essays), verified 2026-10-30: https://martinfowler.com/bliki/MonolithFirst.html and https://martinfowler.com/bliki/MicroservicePremium.html
- Sam Newman, *Building Microservices*, 2nd ed., O'Reilly, 2021 (service decomposition and trade-offs), verified 2026-10-30.
