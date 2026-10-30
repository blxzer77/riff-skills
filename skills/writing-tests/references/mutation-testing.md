# Mutation testing

A mutation tool makes small changes to the code (flip `<` to `<=`, drop a call,
return a constant) and runs the tests against each. If the tests still pass, that
mutant **survived**: there is behavior no test checks. It is the honest answer to
"are these tests good enough?", which coverage cannot give.

## Tools (verified 2026-10-30; check the registry for current versions)

| Language | Tool | Scope to a change |
|---|---|---|
| JS/TS | StrykerJS (`@stryker-mutator/core`) | `npx stryker run --incremental` reuses previous results and tests only changed code |
| Rust | cargo-mutants | `cargo mutants --in-diff <diff-file>` tests only mutants in the diff |
| Python | mutmut | `mutmut run "<module pattern>"`; no diff mode, scope by module |
| Python | cosmic-ray | configure modules in the session config |

## How to use it

1. Run it on the critical module you changed, not the whole codebase; full runs
   can multiply test time by 10–100×.
2. For each survived mutant, decide:
   - A missing behavior test → write the test that kills it.
   - An equivalent mutant (no observable difference) → ignore it.
   - Dead or redundant code → consider removing the code.
3. Report the score with scope, e.g. "pricing.py: 41/45 killed; 4 survivors were
   equivalent".

## Rules

- Do not chase 100%; equivalent mutants make it unreachable and the last points cost
  the most.
- Do not mutate generated code or trivial accessors.
- Without a tool, do it by hand for one critical function: break it in the most
  plausible way and check that a test fails.
