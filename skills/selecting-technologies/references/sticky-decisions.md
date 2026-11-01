# Sticky decisions

Use this for choices that are expensive to reverse: a datastore, language,
framework, hosted service, message broker, public protocol, or data format.

## Before comparing

- Write how you would solve the problem with nothing new. If that works at an
  acceptable cost, it is the answer; check that the real problem is not that
  someone wants to use a particular technology.
- State the must-haves, the cost of being wrong, and the team's ability to run
  the new thing (on-call, backups, upgrades, expertise).

## Compare 2–4 real candidates

Include the current choice or "no change" when it is viable. Drop any candidate
that fails a must-have; do not rescue it with weights.

| Criterion | Question |
|---|---|
| Fit | Does it meet the must-haves on this workload? |
| Added operations | What new process, state, backup, or upgrade does it bring? |
| Maintenance | Recent releases, more than one maintainer, not deprecated (see `checking-facts.md`) |
| Security | Known advisories, secure defaults, update path |
| Familiarity | Has this team run it before? |
| Exit path | How would you move off it, and what must be rewritten? |
| Cost | Current price from the official page, and what scales with use |

Write one sentence of evidence per judgment, or "unknown". Keep fit (how well it
solves today's problem) apart from confidence (how strong the evidence is).

## When evidence is missing

If the decision depends on an unmeasured workload or an unknown exit path,
recommend a time-boxed spike behind a small interface and the result that would
change the decision. Do not migrate on a promise.

## Record it

A choice that adds a hosted dependency, changes a data format or public contract,
or would take more than a few days to undo gets an ADR: the context, the
candidates and why each lost, the facts checked with dates, and the exit path.
