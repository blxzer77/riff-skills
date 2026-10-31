# Evaluation results

> Historical benchmark recorded: 2026-10-30
> Agent/model: Pi default configuration
> Baseline: same prompts without the skill
> Runs: two repetitions per eval case
>
> Current policy (2026-10-31): run new evaluations only with local cometix and
> `deepseek-flash`; do not compare these results directly with the historical Pi run.

## Treatment-aware confirmation (2026-10-31)

These are the first results from the treatment-aware harness (`ef6c8c5`): a
with-skill run counts only when its transcript proves the skill loaded; timeouts,
API errors, invalid grading, and untreated runs are excluded from the treatment
effect and reported separately. Each row is one case with three low-concurrency
runs per configuration. Results are directional evidence, not statistical proof.

| Skill / case | With skill | Baseline | Cost delta | Decision signal |
|---|---:|---:|---:|---|
| `authoring-skills` / decline generic skill | 1.00 | 0.00 | -9.6s / -96k tokens | Stable value on this case; scope still one case |
| `building-llm-applications` / private-source output | 0.89 | 0.89 | +10.0s / +99k tokens | Pass-both; no measured value |
| `designing-apis` / retryable export | 1.00 | 0.33 | +14.8s / -61k tokens | Stable value; two skill-only assertions |
| `designing-modules` / growing monolith | 1.00 | 1.00 | +5.1s / +56k tokens | Pass-both; case does not discriminate |
| `reviewing-code` / parser-client SSRF | 0.73 | 0.80 | +68.0s / +335k tokens | No value; slight regression |
| `reviewing-designs` / overbuilt project | not treated | 1.00 | — | Description did not load skill; no body conclusion |
| `selecting-technologies` / small project | 1.00 | 1.00 | +75.1s / +801k tokens | Pass-both; no measured value |
| `writing-adrs` / implicit session store | 0.89 | 0.00 | +309.6s / +2.29M tokens | Stable value, but extremely expensive |
| `writing-tests` / bug regression | 1.00 | 0.56 | +13.1s / +128k tokens | Process assertion skill-only |

A pass-both result means the case did not demonstrate incremental skill value; it
does not prove the skill is useless. Before removal, replace the case with a harder,
implicit case that the baseline demonstrably fails. If the replacement also shows no
stable gain while adding cost, removal or merging is rational. `reviewing-code` is
not retained as a proven value case: its earlier apparent SSRF gain disappeared
under repeated treatment-aware grading.

The timeout/error policy and stable assertion IDs are part of the harness, not a
claim that the model is deterministic. Retry counts and all-attempt costs are
recorded; a final successful retry remains usable but its retry cost is included.

## Pre-treatment content-revision benchmark (historical, not directly comparable)

All runs below used the local cometix adapter with `deepseek-flash`, one run per
case, and a fresh sandbox per configuration. These are directional results, not
statistical conclusions.

| Skill / scope | With skill | Baseline | Interpretation |
|---|---:|---:|---|
| `authoring-skills`, decline generic skill | 1.00 | 0.00 | New guardrail prevented a generic skill artifact; one case only |
| `building-llm-applications`, 4 cases | 0.92 | 0.75 | Private-source and simple-first cases added value |
| `building-llm-applications`, revised RAG case | 1.00 | 0.67 | Split retrieval-quality and answer-quality evaluation was primary-only |
| `designing-apis`, 3 cases | 1.00 | 0.89 | Retry/authorization/old-client validation was primary-only |
| `reviewing-code`, 3 fixture cases | 1.00 | 0.93 | Concrete parser/client SSRF finding was primary-only |
| `reviewing-designs`, 3 cases | 1.00 | 1.00 | No measured quality delta; with-skill cost was higher |
| `writing-adrs`, 4 cases | 1.00 | 0.70 | Implicit shared-session-store decision was primary-only |
| `writing-tests`, original 4 cases | 0.67 | 0.67 | Bug-fix process value appeared, but total score was flat |
| `selecting-technologies`, final 3 cases | 0.89 | 0.89 | No measured quality delta; with-skill cost was higher |
| `writing-tests`, targeted feature/refactor rerun | 0.50 | 0.50 | Refactor assertion failed in both configurations; not discriminating |

The `reviewing-code` fixture suite now includes authorization/cache, migration, and
URL-parser boundary cases. Its with-skill cost was approximately `+161k` tokens and
`+17s` per case aggregate. The `reviewing-designs` run added approximately `+85k`
tokens and `+19s` with no quality delta, so no further expansion is planned there.

The first `selecting-technologies` run included a popularity-resistance case that
both configurations passed while the skill used about `+1.45M` tokens and `+170s`.
That case was removed as a non-discriminating output eval; the similar query remains
useful for trigger testing. The final three-case rerun remained at baseline parity
while adding about `+210k` tokens and `+49s`.

The `designing-modules` run is excluded: all with-skill cases finished without
loading the skill, so it measures description discovery rather than output quality.

## Current trigger evidence

The revised formal description for `writing-tests` produced `15/20` on an exploratory
run (`train` `9/12`, `validation` `6/8` among completed runs), with two provider/agent
errors excluded. Candidate descriptions reached `11/12` on train but scored worse on
validation (`5/8` with two false positives), so they were not adopted. The formal
description remains the validation-selected version.

The `evaluating-skills` baseline case for writing trigger queries timed out twice at
1200 seconds. It is excluded rather than treated as a skill failure. The current
benchmark policy does not infer quality from incomplete baseline runs.

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
