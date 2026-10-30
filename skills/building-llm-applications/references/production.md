# Production concerns

## Reliability and safety

Set explicit timeouts and bounded retries. Record model, prompt/template version,
retrieval version, tool schema version, and outcome without logging secrets or private
content unnecessarily. Redact inputs at the logging boundary.

Separate:

- model failure (timeout, refusal, malformed output);
- dependency failure (retrieval, tool, provider);
- policy failure (unauthorized or unsafe action);
- product failure (wrong but well-formed answer).

Each needs a different response and test.

## Cost and latency

Bound input context, output tokens, tool steps, retries, and concurrency. Measure
cache hit rate and staleness before adding semantic or prompt caching. Use a cheaper
model only when evals show the task still meets its quality and safety gates. Route by
task requirements, not by brand or novelty.

## Rollout

Ship behind a reversible path. Start with shadow or limited traffic when the action
is safe to observe. Keep a known-good prompt/model/index/tool configuration and a
rollback trigger. Monitor quality proxies and sampled human review, not only latency
and spend.
