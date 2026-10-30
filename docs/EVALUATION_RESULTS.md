# Evaluation results

> Last updated: 2026-10-30
> Agent: Pi
> Baseline: same prompts without the skill
> Runs: two repetitions per eval case

## `writing-tests`

Iteration 2 benchmark:

| Eval | With skill | Without skill |
|---|---:|---:|
| Bug fix / regression test | 1.00 | 0.67 |
| Feature without an explicit test request | 1.00 | 1.00 |
| Flaky test repair | 1.00 | 0.83 |
| Refactor of untested code | 1.00 | 0.00 |
| **Mean** | **1.00** | **0.62** |

Cost:

- Mean time: 51.90s vs 29.62s (`+22.28s`)
- Mean tokens: 69,566 vs 27,314 (`+42,252`)

Observed value:

- The skill caused the agent to run a new regression test before changing production
  code in the successful run.
- It preserved production expiry semantics while replacing real sleeps with a
  controllable clock.
- It added characterization tests before refactoring previously untested code.
- Mechanical checks tested the agent's tests against the original fixture and against
  plausible wrong implementations.

Caveat: the feature case was easy enough that the baseline also passed. It measures
that the agent can handle the feature, not much incremental skill value. More future
cases should target implicit test obligations and difficult edge cases.

## `writing-adrs`

Iteration 2 benchmark:

| Eval | With skill | Without skill |
|---|---:|---:|
| Add durable queue decision record | 0.88 | 1.00 |
| Supersede polling decision with SSE | 0.90 | 0.90 |
| Do not create ADR for trivial CLI change | 1.00 | 1.00 |
| Implicitly record shared session-store decision | 1.00 | 0.50 |
| **Mean** | **0.94** | **0.85** |

Cost:

- Mean time: 49.88s vs 43.46s (`+6.42s`)
- Mean tokens: 98,505 vs 78,052 (`+20,453`)

Observed value:

- The skill recognized an implicit architectural decision and created an ADR without
  being explicitly asked for one.
- It preserved the project's existing ADR numbering and heading style after the skill
  was tightened to prefer local conventions over its bundled template.
- It distinguished a costly decision from a reversible trivial CLI change.

Caveat: one ADR case still has baseline parity. The benchmark is evidence that the
skill helps with implicit decision capture, not proof that every ADR will be correct.

## Trigger evals

An initial Pi trigger run was made before the final low-concurrency/rate-limit handling
was stabilized:

- `writing-tests`: 11/20 queries passed.
- `writing-adrs`: 15/20 queries passed.

The results showed false positives and false negatives that require description tuning.
They should not be treated as final because the run was concurrent and the provider hit
rate limits in a later output-eval round. Re-run with `--jobs 1`, three repetitions,
and inspect train versus validation separately before changing descriptions.

## Interpretation rules

- A skill is valuable when it improves behavior the user did not explicitly request,
  not merely when it answers an explicit instruction better.
- Assertions that pass in both configurations are non-discriminating; replace them or
  drop them from the value calculation.
- An agent API error or rate limit is not a skill failure. Re-run it and exclude it from
  the benchmark if it remains errored.
- A skill's extra tokens/time are part of its cost. Compare them against the quality
  delta and the severity of failures prevented.
- Results do not transfer between Pi, Nyan, Claude Code, Codex, or different models.
