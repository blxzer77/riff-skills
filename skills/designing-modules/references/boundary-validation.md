# Boundary validation

Use this reference when a proposed module boundary needs evidence that it will remain intact.

## Fitness checks

Add the cheapest check that catches the likely failure:

- forbidden-import rules for dependency direction;
- architecture tests for public API use and forbidden internals;
- contract tests for events or calls between modules;
- ownership checks for schema/table access;
- one end-to-end vertical-slice test per critical capability;
- a change-coupling check from recent commits or representative scenarios.

Run checks in normal CI and make violations actionable: name the edge, the owner, and the approved escape hatch. Do not make a broad “all modules may not depend on all modules” rule without documenting legitimate shared foundations.

## Review questions

1. Can a normal feature change stay within one slice?
2. Does each invariant have one owner?
3. Are contracts smaller and more stable than the implementations behind them?
4. Can the boundary be tested without booting unrelated capabilities?
5. What signal shows the boundary is failing, and who responds?

## Sources

- Neal Ford, Rebecca Parsons, and Patrick Kua, *Building Evolutionary Architectures*, O'Reilly, 2017 (fitness functions), verified 2026-10-30.
- Martin Fowler, “BoundedContext” and “Microservice Premium,” martinfowler.com (boundary and cost trade-offs), verified 2026-10-30: https://martinfowler.com/bliki/BoundedContext.html and https://martinfowler.com/bliki/MicroservicePremium.html
