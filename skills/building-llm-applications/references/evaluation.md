# LLM feature evaluation

Evaluate the task, not the model's prose in the abstract.

## Case shape

Each case records:

- user request and relevant context/fixture;
- expected behavior and explicit non-goals;
- assertions that code can check (schema, citations, tool arguments, authorization,
  refusal, state transition);
- a human/model-judge criterion only when the quality cannot be coded;
- risk level and why this case matters.

Include normal, edge, ambiguous, stale/empty context, prompt-injection-like content,
malformed tool results, and repeated requests. Keep a held-out set when optimizing
descriptions or prompts.

## Baseline and iteration

Run the same cases with the current implementation and the candidate. Capture quality,
latency, token usage, cost, tool calls, errors, and unsafe outcomes. Change one major
variable at a time. Remove assertions that pass in both; investigate assertions that
fail in both. Human review catches omissions assertions did not anticipate.

For subjective grading, blind the comparison when possible and require evidence. Do
not let the judge see which version is expected to win.

## Gates

A release gate should include hard failures (invalid schema, unauthorized action,
missing required citation, leaked secret, wrong tool target) and quality thresholds
for the task. Averages can hide catastrophic tails: inspect high-risk cases and
worst-case outcomes separately.
