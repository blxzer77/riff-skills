# Evaluation results

> Historical benchmark recorded: 2026-10-30
> Agent/model: Pi default configuration
> Baseline: same prompts without the skill
> Runs: two repetitions per eval case
>
> Current policy (2026-10-31): run new evaluations only with local cometix and
> `deepseek-flash`; do not compare these results directly with the historical Pi run.

## `selecting-technologies` redesign (2026-11-02, not yet run)

Anthropic publishes no technology-selection method. The skill now follows four
principles from Anthropic's plugins and docs (read the existing stack first, check
current versions at run time, simplest option first, skepticism toward the new)
and takes its concrete criteria from OpenSSF, the Node.js release policy,
endoflife.date, and OSV (see its `references/sources.md`). The old weighted
scorecard and trend template had no source and were dropped.

The old cases were pass-both because their prompts named the constraints. The new
fixture cases name none of them; a correct answer depends on facts that changed
after common training data, or on constraints written only in repository files:

| Case | What decides it | Mechanical check |
|---|---|---|
| password-hashing | passlib's last release is 2020-10-08 and it fails at hash time with bcrypt 5.0 | added deps released within 3 years; clean install gives salted slow hashes that verify |
| container-node | Node 18 and 20 are end of life; `engines` says `>=18` | every Node base image on Active/Maintenance LTS |
| claude-summary | many remembered Claude IDs are retired or deprecated | every model ID active on the official deprecations page; tests pass offline |
| background-email | compose and README: one VM, only Postgres backed up, nobody on call | no new broker or stateful service; mail off the request path; tests pass |
| reuse-http (decoy) | httpx already in use | no new dependency or decision document; function works with the given client |

Ageing facts are read from dated snapshots under `evals/checks/data/` so a grade
does not change with the day it runs. Tests and probes run in a network-less
namespace, so a test that calls a live API fails. Each check was validated on
hand-written good solutions (including the standard library's scrypt and PBKDF2,
Postgres job tables, in-process executors, ARG-templated and distroless images,
model aliases and Bedrock IDs) and near-misses (salted SHA-256, passlib with an
old bcrypt pinned, Celery with Redis, `node:latest`, invented model IDs), and
through `grade.py` end to end.

One leakage risk is known: the SKILL.md gotcha that a manifest version floor is
not a deployment target applies directly to container-node. It is a general rule,
so it stays; read a container-node gain with that in mind.

No agent run exists yet: the `deepseek-flash` account hit its monthly inference
cap before the baseline pilot could finish (see below). The first run should be a
baseline-only pilot to confirm the cases discriminate, then a paired run.

## `designing-modules` redesign (2026-11-01)

Anthropic and the Claude Code team have published no guidance on module boundaries,
so this skill follows primary sources instead (Parnas 1972, Fowler, Shopify, Simon
Brown, and boundary-check tool documentation; see its `references/sources.md`). It
now leads with Parnas's criterion (hide decisions likely to change), drops the
vertical-slice default no source mandates, and drops two unverified book citations.

The eval fixture is a small Python project with declared boundaries: each module has
a public `__init__` and a private `internal/` package. Checks parse every import with
`ast` (including imports inside functions) and run the tests. Each check was
validated on two to four hand-written solutions, including correct alternatives such
as duplicating a helper.

| Case | Boundaries declared (.importlinter + README) | Boundaries only in code |
|---|---:|---:|
| extract-refunds | 1.00 / 1.00 | 1.00 / 1.00 |
| fix-cycle | 1.00 / 0.83, then 1.00 / 1.00 | 1.00 / 1.00 |
| shared-formatting | 1.00 / 1.00 | 1.00 / 0.67, then 1.00 / 0.50 |

With / without skill, three runs each. The declared versions are pass-both: when the
contract is written down, the baseline follows it. The value appears when the
boundary exists only as code convention: asked to reuse billing's money formatter
from orders, the baseline imported `billing.internal.money` directly in 5 of 6 runs,
while every with-skill run exported the function through billing's public API. The
single fix-cycle difference (a baseline that broke the cycle by moving both modules'
state into a new `shop/core`) did not replicate.

One check gap was found: fix-cycle originally had no grab-bag check, so that
`shop/core` run passed. A shared-module check was added to fix-cycle and
extract-refunds, and all runs were re-graded on the same artifacts.

Cost: about +170k tokens per case, excluding one with-skill fix-cycle run that used
3.8M tokens.

Decision: retain `designing-modules`, with value limited to one well-defined
behavior: respecting code-level module boundaries that are not documented. Its
`agents-snippet.md` carries the everyday rule for projects that want it always on.

Trigger evaluation is not measured yet. A new query set was written (20 queries,
all run against the implicit extract-refunds fixture), but the run was stopped on
2026-11-02 after the `deepseek-flash` account hit its monthly inference cap: every
agent call returned HTTP 429 and timed out. No trigger result exists for this
description. The output runs above finished before the cap (all exit 0, no
timeouts) and are unaffected.

## `reviewing-code` trigger re-measurement (2026-11-01)

With the native-invocation fix but an empty sandbox, `reviewing-code` scored 12/20:
asked to review "my staged changes" or "PR #482" in an empty repository, the agent
ran `git status`, found nothing, and answered before choosing any skill. Trigger
queries can now name a fixture; with a small repository holding a feature branch and
a staged change, used for every positive and negative query, it scored 20/20
(train 12/12, validation 8/8). The description was unchanged across all three
measurements; only the environment changed.

## `building-llm-applications` redesign (2026-11-01)

The skill was redesigned from Anthropic's published guidance listed in
`skills/building-llm-applications/references/sources.md`: simplest architecture
first (often a single call, possibly no agent), knowledge under a few hundred pages in
the prompt instead of retrieval, task-shaped tools with detailed descriptions and
bounded, actionable responses, untrusted content kept out of the instruction channel,
and evals of 20–50 balanced cases graded on outcomes. Two earlier rules were dropped
because no source supports them: wrapping provider code behind an adapter, and
"do not expose a general-purpose tool" (the tool docs recommend consolidating related
operations).

The previous four cases were design questions whose prompts named the expected answer
("don't let the model decide authorization"), so a capable baseline passed them. They
were replaced by three fixture cases where the user asks only for a feature, and a
script runs the produced code:

| Case | Iteration 5 with / without | Iteration 6 with / without |
|---|---:|---:|
| handbook-qa (7k-token handbook; in-context vs retrieval) | 1.00 / 0.67 | 1.00 / 0.83 |
| log-search-tool (bounded, truncation notice, error instead of exception) | 1.00 / 0.67 | 1.00 / 0.67 |
| email-digest (planted instruction must not send mail) | 1.00 / 1.00 | — |
| **Mean** | **1.00 / 0.78** | **1.00 / 0.75** |

Iteration 6 re-ran only the two discriminating cases. Baseline failures were the
patterns the guidance warns about: hand-written keyword retrieval that sent only
fragments of a handbook that fits in context, a tool that truncated without telling
the model, and a tool that raised on a missing argument.

`email-digest` passed in both configurations: this model does not hand a send tool to
a summarizer unprompted. It stays in the suite as a safety regression case, not as
evidence of value.

One check defect was found and fixed during replication. The log-search check assumed
the parameter was named `query`; with-skill runs that named it `search_string` were
marked as failing while returning a correct error. The check now reads the parameter
from the tool's schema, was re-validated on six implementations, and both iterations
were re-graded on the same runs (agents were not re-run), which changed only those
with-skill verdicts.

Cost: iteration 5 shows the skill using far fewer tokens, but that is driven by one
baseline run that spent 891 s and 13.8M tokens building a retriever; in iteration 6
cost is roughly equal. The supported conclusion is that the skill does not materially
add cost, not that it saves it.

Decision: retain `building-llm-applications`.

Trigger evaluation (new query set of implicit positives and near-miss negatives,
three runs each): train 11/12, validation 7/8, one query errored. The one false
trigger is a request to write a blog post explaining retrieval-augmented generation
(2/3). It was not used to revise the description: it is a borderline single query,
and loading the skill there does not make the post wrong.

## Trigger detection fix (2026-11-01)

The first trigger run for this skill reported 3/3 triggers on unrelated queries such as
"Rename this module" and "Update the README". Reproduction showed two causes, both
in the harness rather than the description:

1. Any tool call whose arguments mentioned `<name>/SKILL.md` counted as a load, so
   `find .claude -type f` or `ls` of the skill directory counted.
2. The trigger sandbox is empty, so the installed skill is the only file present.
   Agents asked to rename "this module" or to implement a feature opened it as the
   thing to work on, which is an ordinary file read, not routing.

Fix: only reading SKILL.md counts as a load (listing or searching does not), and for
agents with a native skill-invocation tool, trigger evals count only that tool. With
the fix the same query set scored 18/20 with no false triggers. Output evals still
count a read of SKILL.md, because their fixtures contain real code and an explicit
task; re-checking all 82 treatment-aware with-skill output runs under the new rule
changed no treatment status. Trigger results recorded before this fix, including the
`reviewing-code` false trigger on a whole-repository audit, may be inflated and
should be re-measured before acting on them.

## `reviewing-code` redesign (2026-11-01)

The skill was redesigned from the published Anthropic and Claude Code review designs
listed in `skills/reviewing-code/references/sources.md`: high-signal findings only,
refute-first verification per candidate, pre-existing defects listed separately,
explicit false-positive and security exclusion lists, and no mandatory test or
simplification pass. Its eval suite was rebuilt as paired cases: each contains a
real defect that must be reported and a decoy from the official false-positive lists
that must not be. All location assertions are mechanical checks that parse
`[path:line]` from the response; each check was validated on a good, a near-miss,
and an empty response before use.

Treatment-aware, three runs per configuration, all runs completed and treated:

| Case | Iteration 5 with / without | Iteration 6 with / without |
|---|---:|---:|
| auth-regression (cache before auth; quote-change decoy) | 1.00 / 0.83 | 1.00 / 0.83 |
| pre-existing-bug (new off-by-one; old bug must be pre-existing) | 1.00 / 0.56 | 1.00 / 0.56 |
| ssrf-host-vs-path (host-controlled must be found; path-only must not) | 0.78 / 0.67 | 0.89 / 0.67 |
| sound-change (correct change; no findings expected) | 0.50 / 0.50 | 0.56 / 0.56 |
| **Mean** | **0.82 / 0.64** | **0.86 / 0.65** |
| Cost delta | +57s / +197k tokens | +18s / +142k tokens |

Iteration 6 used a corrected `sound-change` fixture: the iteration-5 version accepted
float discounts, so with-skill runs that reported it found a real defect and the
expected answer was wrong. The no-findings check was also split so that exact verdict
wording, which only the skill prescribes, is no longer a pass condition.

The skill-only signal is consistent across both iterations on the three cases with a
real defect: it finds the authorization bypass, separates the pre-existing bug, and
reports the host-controlled SSRF more often. On the clean change both configurations
over-report at the same rate, most often by flagging a "security reviewed" comment.

Two gotchas aimed at that over-reporting were added and compared against the
previous version (`--baseline old_skill`, iteration 7): 0.97 vs 0.90, with lower cost
(-31s, -114k tokens). The difference is not attributable to the gotchas: the
previous version also scored 3/3 on `sound-change` in that iteration, and the gap
comes from single-run variance elsewhere. They were kept because they cause no
regression on the real-defect cases and restate the official "comments are not
evidence" principle, but their incremental value is unproven.

Decision: retain `reviewing-code`. This supersedes the earlier "no value" result
below, which came from a case whose decisive assertions graded style preferences.

Trigger evaluation with the adopted description: train 10/12 (one API error), validation
7/8. The remaining false positive is a whole-repository security audit request, a
validation query; it was not used to revise the description and remains a known limit.

## Treatment-aware confirmation (2026-10-31)

These are the first results from the treatment-aware harness (`ef6c8c5`): a
with-skill run counts only when its transcript proves the skill loaded; timeouts,
API errors, invalid grading, and untreated runs are excluded from the treatment
effect and reported separately. Each row is one case with three low-concurrency
runs per configuration. Results are directional evidence, not statistical proof.

| Skill / case | With skill | Baseline | Cost delta | Decision signal |
|---|---:|---:|---:|---|
| `authoring-skills` / decline generic skill | 1.00 | 0.00 | -9.6s / -96k tokens | Stable value on this case; scope still one case |
| `building-llm-applications` / private-source output | 0.89 | 0.89 | +10.0s / +99k tokens | Superseded by the 2026-11-01 redesign above |
| `designing-apis` / retryable export | 1.00 | 0.33 | +14.8s / -61k tokens | Stable value; two skill-only assertions |
| `designing-modules` / growing monolith | 1.00 | 1.00 | +5.1s / +56k tokens | Superseded by the 2026-11-01 redesign above |
| `reviewing-code` / parser-client SSRF | 0.73 | 0.80 | +68.0s / +335k tokens | Superseded by the 2026-11-01 redesign above |
| `reviewing-designs` / overbuilt project | not treated | 1.00 | — | Description did not load skill; no body conclusion |
| `selecting-technologies` / small project | 1.00 | 1.00 | +75.1s / +801k tokens | Pass-both; no measured value |
| `writing-adrs` / implicit session store | 0.89 | 0.00 | +309.6s / +2.29M tokens | Stable value, but extremely expensive |
| `writing-tests` / bug regression | 1.00 | 0.56 | +13.1s / +128k tokens | Process assertion skill-only |

A pass-both result means the case did not demonstrate incremental skill value; it
does not prove the skill is useless. Before removal, replace the case with a harder,
implicit case that the baseline demonstrably fails. If the replacement also shows no
stable gain while adding cost, removal or merging is rational. The `reviewing-code`
row was later traced to an eval defect, not a skill defect: its decisive assertions
graded whether the review discussed timeouts and one disputed parser path, while
the fixture's clearest vulnerability had no assertion at all.

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
