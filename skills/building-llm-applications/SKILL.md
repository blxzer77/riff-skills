---
name: building-llm-applications
description: Designs and implements reliable LLM-powered features by starting from task requirements and evals, then choosing retrieval, prompts, tools, workflows, safety controls, and cost limits that fit the product. Use when building or changing RAG, tool calling, agent workflows, model routing, context management, generated-output verification, or LLM feature evaluation, including when the user only says an AI feature is unreliable, expensive, or hard to debug. Not for ordinary deterministic features with no model or generated output.
license: Apache-2.0
metadata:
  verified-on: "2026-10-30"
---

# Building LLM applications

Treat a model call as a probabilistic component behind a testable boundary, not as a
replacement for product design. Start with the task and failure cost; add retrieval,
tools, agents, or orchestration only when a simpler call cannot meet the requirement.

## Workflow

- [ ] **Define the task.** Write the user goal, allowed actions, unacceptable
      failures, latency/cost budget, data boundaries, and what must remain
      deterministic. Separate answer quality from action safety.
- [ ] **Create a small eval set before changing prompts.** Include normal, ambiguous,
      adversarial, empty, and stale-data cases. Grade structure/invariants with code;
      use a model judge or human only for qualities that code cannot decide.
- [ ] **Inspect the existing path.** Read prompts, schemas, tool definitions,
      retrieval code, logs, and current evals. Establish a baseline before redesign.
- [ ] **Choose the least complex architecture.** Direct structured output first;
      retrieval for knowledge grounding; one tool loop for external actions; a
      workflow for known stages; multiple agents only when roles or context really
      need separation.
- [ ] **Design boundaries.** Validate model input/output at the application boundary,
      keep tools narrow and typed, make side effects explicit and authorized, and
      keep provider-specific code behind an adapter.
- [ ] **Handle failure.** Define timeouts, retry limits, invalid output behavior,
      stale/missing retrieval, tool errors, refusal, partial execution, and human
      approval for high-impact actions. Never silently turn an uncertain answer into
      a successful action.
- [ ] **Measure and iterate.** Run the baseline and evals after each meaningful
      change; track quality, latency, tokens, cost, tool errors, and unsafe outcomes.
      Keep a rollback path for prompts, models, indexes, and tool schemas.

## Architecture defaults

| Need | Start with | Add complexity when |
|---|---|---|
| Classification/extraction | One model call with a schema and validation | Quality failures need context or a second pass |
| Private or changing knowledge | Retrieval with source references and freshness rules | Retrieval quality is measured and still insufficient |
| External action | One narrow typed tool with authorization and confirmation | A known workflow requires multiple dependent steps |
| Multi-step deterministic process | Application-owned workflow/state machine | Model planning is the actual uncertain task |
| Multiple agents | One agent first | Independent context, ownership, or failure isolation is proven |
| Model/provider choice | Adapter with one default and recorded fallback | Different tasks have measured quality/cost needs |

## Tool and output rules

- Tool descriptions state purpose, required inputs, side effects, authorization, and
  failure shape. Do not expose a giant general-purpose tool.
- Validate arguments before execution and validate results before passing them back.
  Idempotency keys protect retried mutations; read-only tools are the default.
- Keep business decisions in ordinary code when they can be expressed deterministically.
  The model may propose; application code decides whether an action is allowed.
- Return structured outputs with a versioned schema. Treat malformed, incomplete,
  or overconfident output as a handled failure, not as a best-effort success.
- Retrieval answers cite the source chunks used, apply access control before retrieval,
  and state what happens when no sufficiently relevant source is found.

## Evaluation minimum

A useful eval case contains: user task, relevant fixture/context, expected behavior,
checkable assertions, and a reason it is difficult. Compare with a baseline and keep
near-miss cases that should not activate a workflow. Test prompt changes, tool schema
changes, retrieval changes, and model changes separately when possible.

## Gotchas

- More context can reduce quality. Measure retrieval precision and context length;
  do not append the whole repository or conversation by default.
- A tool call that succeeds technically can still be unsafe or semantically wrong.
  Verify authorization, target, idempotency, and result before reporting success.
- A model's refusal, timeout, or malformed JSON is an expected branch to test, not an
  exceptional branch to hide.
- Prompt tweaks without a baseline and evals are vibes. Keep the change, evidence,
  and regression result together.
- Token cost is part of architecture. Bound context, output, retries, and tool loops;
  cache only when stale data and key scope are understood.
- Do not put secrets or untrusted instructions into a prompt and assume the model
  will treat them as policy. Keep authority in application code and permissions.

## References

- `references/evaluation.md` — task-specific eval design and regression loop.
- `references/retrieval.md` — retrieval boundaries, freshness, citations, and failure.
- `references/tools-and-workflows.md` — tool schemas, orchestration, and side effects.
- `references/production.md` — cost, latency, safety, observability, and rollout.
- `assets/agents-snippet.md` — always-on project rule for LLM features.
