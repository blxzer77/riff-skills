# Test strategy

Contents: [Sizes](#sizes) · [Shape](#shape) · [Contract tests](#contract-tests) · [Snapshot tests](#snapshot-tests) · [New project checklist](#new-project-checklist)

## Sizes

Classify tests by what they are allowed to do, not by how much code they touch
(Software Engineering at Google, ch. 11, https://abseil.io/resources/swe-book/html/ch11.html):

| Size | Allowed | Typical use |
|---|---|---|
| Small | one process; no sleep, network, or disk | logic, pure functions, in-memory fakes |
| Medium | one machine; localhost services, a real DB in a container | handlers, repositories, framework wiring |
| Large | multiple machines or real external services | a few critical end-to-end flows |

Write the smallest test that gives confidence in the behavior.

## Shape

Two well-known shapes disagree on where most tests should sit:

- **Pyramid** (Mike Cohn; Ham Vocke, https://martinfowler.com/articles/practical-test-pyramid.html):
  many fast unit tests, fewer integration tests, very few end-to-end. Push tests as
  low as they can go.
- **Trophy** (Kent C. Dodds, https://kentcdodds.com/blog/write-tests): static
  analysis as the base, then mostly integration tests, because they resemble real
  use and give more confidence per test.

Both agree: do not test implementation details, and keep end-to-end tests few. Pick
by where the risk lives:

| Codebase | Weight toward |
|---|---|
| Libraries, algorithms, domain logic, parsers | unit tests (pyramid) |
| Web apps and services where most code is glue between framework, DB, and UI | integration tests (trophy) |
| Thin CRUD over a framework | a few integration tests per endpoint; little unit testing |

Static types and linters count as the cheapest test layer; turn them on first.

## Contract tests

Consumer-driven contract tests (e.g. Pact, https://docs.pact.io/getting_started/what_is_pact_good_for)
fit when you control both consumer and provider and have a few consumers. They do
not fit public APIs with unknown consumers, pass-through APIs, or functional testing
of the provider. For a single repo deploying both sides together, an integration
test is simpler.

## Snapshot tests

Useful for large, stable outputs (rendered markup, CLI output, generated files).
Keep snapshots small, make output deterministic (fixed dates and IDs), name them,
review every snapshot diff like code, and never regenerate to make a failure go
away (Jest docs, https://jestjs.io/docs/snapshot-testing). They complement, not
replace, behavior assertions.

## New project checklist

- [ ] Use the ecosystem's default runner (pytest, vitest/node:test, cargo test, go test).
- [ ] Turn on the type checker and linter in the same command as the tests.
- [ ] One example test per layer you will use, as a pattern to copy.
- [ ] A fast default command (small + medium tests) that runs in seconds to a minute.
- [ ] A test database or service strategy decided once (containers, in-memory fake).
- [ ] Add `assets/agents-snippet.md` to the project's `AGENTS.md`.
