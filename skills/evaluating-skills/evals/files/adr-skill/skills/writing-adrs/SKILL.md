---
name: writing-adrs
description: Writes and maintains Architecture Decision Records that capture the context, real alternatives, chosen option, and honest consequences of a technical decision. Use when the user asks for an ADR or decision record, and also whenever a change adds or replaces a framework, library, datastore, or external service, alters module or API boundaries, or settles a cross-cutting approach, even if nobody mentions ADRs. Not for general design documents or README updates.
license: Apache-2.0
---

# Writing ADRs

An ADR exists so that a future reader, often an agent with no memory of today, can
tell *why* the system is the way it is and when that reason stops holding. Without
it they either preserve a decision blindly or reverse it blindly.

## When a decision needs an ADR

Write one when the decision is costly to reverse. Any one of these qualifies:

| Signal | Examples |
|---|---|
| New or replaced dependency with lock-in | framework, ORM, datastore, queue, auth provider, LLM provider, hosting |
| Boundary change | splitting or merging modules, packages, services; moving ownership of data |
| Contract change | public API shape, versioning approach, event or file formats, DB schema strategy |
| Cross-cutting approach | error handling, auth model, state management, concurrency, caching, observability |
| Deliberate deviation | choosing *not* to follow a project convention or a common practice |
| First of its kind | something this codebase has not done before |

Skip it for choices that are cheap to undo or fully determined by existing
conventions (a helper's name, a library already standard in the project).
When unsure, write a short one; a three-paragraph ADR is cheap, rediscovering lost
rationale is not.

If you make such a decision while doing other work, say so and write the ADR in the
same change. Do not ask the user whether to record it; ask only about facts you lack.

## Workflow

- [ ] Find existing ADRs (`docs/adr/`, `doc/adr/`, `docs/decisions/`, `adr/`, or
      search for files containing "## Decision"). Follow their location, numbering,
      template, and language. Only if none exist use `docs/adr/` and
      `assets/adr-template.md`.
- [ ] Read related ADRs; the new one may supersede or depend on them.
- [ ] Gather facts: current state, constraints, and what forced the decision now.
      Check versions, licenses, and maintenance status of options against their
      official sources; do not rely on memory.
- [ ] List at least two real options. "Do nothing" counts only when it is viable.
- [ ] Write the ADR (rules below). Status is `proposed` unless the user has already
      agreed to the decision or asked you to implement it, then `accepted`.
- [ ] If it replaces an older decision, set the old ADR's status to
      `superseded by NNNN` and link both ways. Never rewrite an accepted ADR's
      decision; supersede it.
- [ ] Update the index if the project keeps one (`README.md` in the ADR directory).
- [ ] Run the checklist at the end.

## Writing rules

- **One decision per ADR.** If the text decides two things, split it.
- **Title**: number plus short noun phrase naming problem and choice:
  `0007. Use PostgreSQL for job queue state`.
- **Filename**: `NNNN-kebab-title.md`, four digits, next free number, never reused.
- **Context states facts, neutrally.** It must not argue for the winner. Name the
  quality attributes at stake.
- **Drivers before options.** If the criteria are just the winner's features
  restated, the analysis is backwards; derive criteria from the problem.
- **Options are real.** A strawman ("write our own database") is not an alternative.
  Say why each loser lost.
- **Decision** says "We will …" and *why*, referring to the drivers. It must say
  more than the title.
- **Consequences include at least one cost**, and who pays it (users, operators,
  future maintainers, API clients). Note follow-up decisions this forces.
- **Confirmation**: how compliance can be checked, ideally automatically (a test,
  lint rule, dependency constraint, architecture test).
- **Short.** One to two pages. Detailed design goes in code or a design doc and is
  linked. State your confidence if the evidence is thin.
- **Plain, factual language.** No marketing adjectives; every claim should survive
  "how do you know?".

## Lightweight form

For small but significant decisions, or to record a decision already made in code,
a Y-statement inside the template's Decision section is acceptable:

> In the context of <situation>, facing <concern>, we decided for <option> and
> against <other options>, to achieve <quality>, accepting <downside>.

## Checklist

- [ ] Context would let a newcomer understand the problem without the code.
- [ ] Two or more real options, each with the reason it won or lost.
- [ ] At least one negative consequence, with who bears it.
- [ ] Decision text explains why, not just what.
- [ ] Status, date, number, and supersession links are correct.
- [ ] Nothing in it is a guess presented as fact.

## Gotchas

- Backfilling an ADR for an existing choice: date it today, say it records a past
  decision, and reconstruct rationale from commits, issues, and code; mark
  uncertain reasons as such rather than inventing them.
- An ADR that only lists pros reads as a sales pitch and will be ignored the first
  time the costs show up. The cost section is the part future readers need most.
- Editing an accepted ADR's decision destroys the history it exists to keep.
  Typos and links are fine; changed decisions get a new ADR.
- Projects often keep the habit only if it is always-on. Offer
  `assets/agents-snippet.md` for the project's `AGENTS.md` when the project has no
  ADRs yet.

## Files

- `assets/adr-template.md` — default template (MADR-based); copy when the project has none.
- `assets/agents-snippet.md` — paste into a project's `AGENTS.md` to make ADRs a habit.
