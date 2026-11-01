---
name: designing-modules
description: Draws, enforces, and changes module boundaries in an existing codebase, proportionate to its size and team, so features can change without reaching into each other's internals. Use when splitting or extracting a module, moving code between modules, fixing modules that import each other's internals or each other in a cycle, adding boundary checks, or deciding whether to introduce packages or services, even if the user only says the code is tangled or hard to change. Not for object-oriented design lessons, choosing a technology, or designing an HTTP API.
license: Apache-2.0
metadata:
  verified-on: "2026-11-01"
---

# Designing modules

A module hides a design decision that is likely to change behind an interface that
reveals as little as possible. That is what lets one part change without the rest
changing with it. A directory is not a module; a boundary exists only where callers
are kept from depending on what is behind it.

## Workflow

- [ ] **Read the existing structure first.** Find how the project already declares
      boundaries: package public APIs (`__init__` exports, `index` files, `pub`,
      exported names), `internal` or private directories, boundary-check
      configuration (import-linter, dependency-cruiser, ArchUnit, Packwerk, module
      visibility rules), per-directory ownership, and which module owns which data.
      Follow those conventions; do not introduce a second scheme.
- [ ] **Name what should change independently.** For a split or extraction, list
      the decisions likely to change (a pricing rule, a storage format, a provider)
      and the code that changes together today. Group by what changes together; one
      module per hidden decision, not one per noun or layer.
- [ ] **Define the public interface before moving code.** Decide what callers may
      use, keep everything else private, and give each module sole ownership of its
      data. Other modules reach that data only through the owner's interface.
- [ ] **Move incrementally.** Introduce the new interface, switch callers to it,
      then move the implementation and delete the old path. Keep the build and tests
      passing at each step. Read `references/migration.md` for a replacement or an
      extraction that cannot be done in one change.
- [ ] **Check the boundary mechanically.** Run the project's boundary checks, or add
      the smallest one that would catch the likely regression (forbidden imports,
      no cycles, protected internals). Read `references/boundary-checks.md`.
- [ ] **Stop when the next split has no reason.** A boundary without an
      independently changing decision, owner, or data only adds indirection.

## Choosing the scale

| Situation | Default | Move up when |
|---|---|---|
| Small codebase, one team, one deploy | One deployable with clear internal modules | Unrelated changes keep colliding in the same files |
| Growing codebase, shared deploy | Modular monolith: modules with public interfaces, owned data, and enforced boundaries | A module needs independent scaling, release cadence, failure isolation, or ownership by another team |
| A proven independent need | Extract only that capability as a service | — |

Start with a monolith even when you expect it to grow; service boundaries are hard
to get right early and much harder to move once drawn. Services do not fix a tangled
codebase: if modules breach each other in one process, they will breach each other
over the network, at higher cost. Read `references/scale.md` before proposing a new
service or package.

## Gotchas

- Reaching into another module's internals or tables because it is the quickest way
  to the data is the most common way boundaries erode. Add or use a public function
  on the owning module instead, even if it is one line.
- A shared `utils` or `common` package that several modules import becomes a module
  everyone depends on and no one owns. Put a helper in the module that owns its
  concept and export it, or duplicate a few lines.
- An import cycle means neither module can be understood or changed alone. Break it
  by moving the shared concept into one side or by inverting the dependency through
  an interface, not by deferring the import inside a function.
- Decoupling alone can harden a bad split: if a typical change still edits several
  modules, the boundary is in the wrong place. Measure by whether code that changes
  together lives together.
- Code that moved but is still reached through its old internal path has not been
  extracted. Update callers to the new public interface and remove the old access.

## References

- `references/boundary-checks.md` — read when adding or running a mechanical check on imports, cycles, or data access.
- `references/migration.md` — read when replacing an implementation or extracting a module across several changes.
- `references/scale.md` — read before proposing a new package or service.
- `references/sources.md` — the published sources this skill follows.
- `assets/agents-snippet.md` — copy into the project's agent instruction file so everyday feature work respects module boundaries.
