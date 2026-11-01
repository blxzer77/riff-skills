# Boundary checks

Verified on 2026-11-01. Tools and contract types from the sources in `sources.md`.

A boundary that is not checked erodes: it is too easy for the next change to import
whatever is closest. Prefer a static check over runtime call tracing; it is fast
enough to run on every change and reports the exact offending import.

## What to check

| Rule | Catches |
|---|---|
| Protected internals: only the owning module may import `<module>.internal` | Reaching past a module's public interface |
| No cycles among sibling modules | Modules that cannot be understood or changed alone |
| Independence: listed modules may not import each other, directly or indirectly | Features coupled through each other |
| Forbidden: lower layers or shared code may not import a feature module | Dependencies pointing the wrong way |
| Data ownership: a module queries only the tables or collections it owns | Shared-database coupling |

## Tools by ecosystem

- Python: import-linter contracts (`protected`, `independence`, `acyclic_siblings`,
  `forbidden`, `layers`).
- JavaScript and TypeScript: dependency-cruiser rules such as forbidding imports
  between feature folders and detecting circular dependencies.
- Java and JVM: ArchUnit tests for layers, cycles, and package access.
- Ruby: Packwerk package visibility and dependency checks.
- Languages with access control: make internals non-exported (unexported names,
  package-private, `internal`), so the compiler enforces the boundary.

When the project has no tool and adding one is not appropriate, a short test that
parses imports and asserts the rule is enough, and is better than none.

## Making checks useful

Run the check in normal CI. Report the offending file, the import, and the rule it
breaks. Record intentional exceptions in the configuration with a reason rather than
weakening the rule.
