---
name: designing-modules
description: Designs maintainable module boundaries and chooses an architecture proportionate to a project's size, constraints, and team. Use when splitting a codebase, deciding whether to introduce services, organizing vertical slices, or planning a modularity migration. Not for generic object-oriented design lessons or choosing a technology without examining the repository.
license: Apache-2.0
metadata:
  verified-on: "2026-10-30"
---

# Designing modules

Choose the smallest architecture that makes the next change safer. A module is a boundary for ownership, dependencies, tests, and change; it is not merely a directory.

## Workflow

- [ ] **Inspect before proposing.** Read the repository map, build/package manifests, entry points, deployment topology, test layout, dependency graph, recent change hotspots, and contributor/ownership signals. Ask for missing constraints: team boundaries, deployment needs, reliability targets, data ownership, and expected growth.
- [ ] **Name the pressure.** Record the concrete pain (coupled changes, slow tests, unclear ownership, independent scaling, fault isolation, or release coordination) and at least one representative change that currently crosses boundaries. Do not split for aesthetics.
- [ ] **Choose the scale rung.** Start at the lowest rung that addresses the pressure: single module, modular monolith, or services. Use the ladder in `references/scale-and-boundaries.md` when the choice is disputed.
- [ ] **Sketch vertical slices.** For each proposed module, identify one end-to-end capability, its public API/events, owned data and invariants, allowed collaborators, and tests. Keep UI/request handling, application behavior, and persistence for a capability together unless a real constraint requires otherwise.
- [ ] **Set dependency direction.** Make dependencies point toward stable policy and explicit contracts. Reject cycles; keep infrastructure at the edge; expose narrow interfaces rather than internal tables, classes, or utilities. Document intentional exceptions.
- [ ] **Plan the smallest migration.** Prefer branch by abstraction for an internal replacement and a strangler path for an extracted capability. Include compatibility seams, dual-read/write risks, rollout and rollback, and deletion criteria. Read `references/migration.md`.
- [ ] **Validate the boundary.** Add boundary tests or fitness checks that fail when forbidden imports, data access, or API coupling returns. Test the highest-risk contract and one real vertical path. Read `references/boundary-validation.md`.
- [ ] **Stop or revise.** Stop splitting when a boundary has no independent change, ownership, data, deployment, or failure reason; when indirection exceeds the benefit; or when tests show the proposed interface is unstable. Consolidate instead of preserving a bad split.

## Decision rules

| Evidence | Default | Avoid |
|---|---|---|
| Small codebase, one team, one release cadence, low operational pressure | One module with clear internal seams | Service scaffolding and speculative layers |
| Growing codebase, recurring cross-feature breakage, shared deployment | Modular monolith with enforced boundaries | “Modules” that freely import each other |
| Genuine independent scaling, ownership, availability, compliance, or release needs | Extract only the capability that has that need | Distributed systems as a substitute for code organization |
| Boundary is hard to name or requires shared mutable state | Delay extraction; make the seam observable first | Splitting by technical layer or noun alone |

A service boundary is justified by an operational or ownership constraint, not by a desired diagram. Prefer a synchronous in-process call while the same process and release are sufficient; make the contract explicit so extraction remains possible.

## Required design record

Return a short decision record, not a catalog of patterns:

```markdown
## Module decision
- Pressure and evidence:
- Current scale and constraints:
- Chosen rung:
- Modules / vertical slices:
- Public contracts and owned data:
- Dependency direction and forbidden edges:
- Boundary checks:
- Migration and rollback:
- Stop signals / revisit date:
```

## Gotchas

- A folder named `module` is not a boundary. Verify imports, data access, ownership, and tests enforce it.
- Shared databases erase service ownership. If extraction is not needed yet, say so; if it is, assign ownership and a transition plan before adding a network call.
- “Reuse” across modules can create a hidden coupling. Prefer a small stable contract; duplicate trivial code when it prevents synchronized changes.
- A clean dependency graph does not prove a useful boundary. Check whether a normal feature change stays inside one vertical slice.
- Stop signals are deliverables: record what would trigger consolidation or extraction rather than leaving architecture open-ended.

## References

- `references/scale-and-boundaries.md` — read when selecting the architecture rung or challenging a proposed split.
- `references/migration.md` — read when changing an existing boundary or extracting code incrementally.
- `references/boundary-validation.md` — read when implementing import, contract, ownership, or fitness checks.
