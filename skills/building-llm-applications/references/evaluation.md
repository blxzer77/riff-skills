# Evaluating an LLM feature

Verified on 2026-11-01. Adapted from the evaluation guidance in `sources.md`.

Evals are how you know whether a change helped. Build them before tuning prompts.

## Cases

- Start with twenty to fifty tasks taken from real failures or real user requests.
  Early changes have large effects, so a small set is enough to see them.
- A good case is one where two domain experts would independently reach the same
  pass/fail verdict. Ambiguous cases add noise, not signal.
- Balance the set: include cases where the feature should act and where it should
  decline, return no answer, or do nothing. One-sided sets reward over-eager
  systems.
- Include the hard edges: empty or irrelevant context, conflicting sources, malformed
  input, planted instructions, and the largest realistic input.

## Grading

Prefer, in order: code checks (schema valid, field equals expected, tool not called,
state changed), then model graders with a rubric, then human review. Grade the
outcome the system produced rather than the exact steps it took; capable systems
find valid paths the author did not anticipate.

For model graders, use one clear rubric per dimension, allow an "unknown" verdict
when the evidence is missing, and check a sample of verdicts against human judgment
before trusting the score.

## Running

- Run each case in a fresh context. Shared state between trials inflates scores.
- Run each case several times. Report how often it passes, and for actions that must
  never go wrong, whether it passes every time.
- Read transcripts of failures and of surprising passes; the score says what
  happened, the transcript says why.

## Retrieval

Evaluate retrieval separately from the answer: did the right passages come back
(recall, precision, rank of the first relevant one), and did the answer use them.
Otherwise a wrong answer cannot tell you which layer to fix.

## Deciding

Compare against the current version on the same cases. Keep a change when it
improves the measured outcome by more than it adds in cost and latency, and keep
the cases that guard against regressions in the suite.
