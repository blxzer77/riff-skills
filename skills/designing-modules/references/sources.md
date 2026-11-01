# Sources

Anthropic and the Claude Code team have not published guidance on where to draw
module boundaries; their material on large codebases covers loading context per
directory, not code structure. This skill therefore follows the primary sources
below. All pages were fetched on 2026-11-01.

| Source | What this skill takes from it |
|---|---|
| D. L. Parnas, "On the Criteria To Be Used in Decomposing Systems into Modules", CACM 15(12), 1972 | Decompose by design decisions likely to change; each module hides one; interfaces reveal as little as possible |
| Martin Fowler, MonolithFirst (2015) | Start with a monolith built with modularity at the API and data boundaries; boundaries are hard to get right early; evidence is tentative |
| Martin Fowler, MicroservicePremium (2015) | Services only when the system is too complex as a monolith; in practice monolith boundaries are easily breached |
| James Lewis and Martin Fowler, Microservices (2014) | Remote calls are expensive and need coarser interfaces; moving code across service boundaries is hard |
| Martin Fowler, BoundedContext (2014) | One model per context; boundaries follow how people and teams use the language |
| Martin Fowler, StranglerFigApplication (2024) and BranchByAbstraction (2014) | Gradual replacement with the system working at every step; delete the old path |
| Shopify Engineering, "Deconstructing the Monolith" and "Under Deconstruction" | Components with a public API and exclusive data ownership; violations as access outside the public API; change locality; decoupling alone can harden a bad split; static checks over runtime tracing |
| Simon Brown, "Modular monolith" | Poorly built monoliths will not become good services; use language access control to enforce boundaries |
| import-linter `2173911`, dependency-cruiser `96a1dd3`, ArchUnit `0aa50c0`, Packwerk `31e5342` | Contract types for protected internals, independence, acyclic siblings, forbidden and layered imports |

URLs:

- https://www.cs.colostate.edu/~france/CS314/Readings/Parnas-decomposition.pdf
- https://martinfowler.com/bliki/MonolithFirst.html
- https://martinfowler.com/bliki/MicroservicePremium.html
- https://martinfowler.com/articles/microservices.html
- https://martinfowler.com/bliki/BoundedContext.html
- https://martinfowler.com/bliki/StranglerFigApplication.html
- https://martinfowler.com/bliki/BranchByAbstraction.html
- https://shopify.engineering/deconstructing-monolith-designing-software-maximizes-developer-productivity
- https://shopify.engineering/shopify-monolith
- https://simonbrown.je/modular-monolith/
- https://github.com/seddonym/import-linter
- https://github.com/sverweij/dependency-cruiser
- https://github.com/TNG/ArchUnit
- https://github.com/Shopify/packwerk
