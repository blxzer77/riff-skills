---
name: building-llm-applications
description: Designs and implements LLM-powered features with the least complex architecture that meets the task, then hardens them with tool design, retrieval choices, injection defenses, and evals. Use when building or changing anything that calls a language model, including extraction, classification, RAG, tool calling, agents, or multi-agent workflows, and when an AI feature is unreliable, too slow, too expensive, or hard to evaluate, even if the user names only a framework or a vector database. Not for ordinary features with no model call, or for choosing a model vendor alone.
license: Apache-2.0
metadata:
  verified-on: "2026-11-01"
---

# Building LLM applications

Start with the simplest thing that can meet the requirement, and add complexity only
when an eval shows it helps. Most features that look like they need an agent are
served by one well-prompted model call, sometimes with retrieved context and a few
examples. Every extra stage adds latency, cost, and a new way to fail.

## Workflow

- [ ] **Define success.** Write down the task, inputs, what counts as correct, the
      cost of a wrong answer or wrong action, and latency and cost budgets. Make the
      criteria measurable: a schema, an accuracy target on a labeled set, a refusal
      rate, a cost per request.
- [ ] **Build a small eval set first.** Collect real or realistic cases, including
      ones that should succeed and ones that should be refused, return nothing, or
      take no action. Twenty to fifty cases drawn from real failures is enough to
      start. Read `references/evaluation.md`.
- [ ] **Choose the lowest rung** that meets the criteria (table below). Use the
      provider's API directly before adding a framework; a framework hides the
      prompts and responses you need to debug.
- [ ] **Design the boundaries.** Validate model output in code before acting on it.
      Keep authorization and irreversible decisions in application code. Treat
      every piece of third-party content as data. Read `references/tools.md` when
      the model calls tools and `references/injection.md` when it reads content you
      do not control.
- [ ] **Measure, then move up a rung only if the eval says so.** Record quality,
      latency, tokens, and failures per case. Keep the change only when it improves
      the measured outcome by more than it costs.

## Choosing the architecture

| Rung | Use when | Move up when |
|---|---|---|
| One model call with a schema, examples, and validation | The task is a single transformation: extract, classify, summarize, draft | The eval shows the call cannot meet the criteria even with better instructions and examples |
| Knowledge in the prompt | The reference material fits comfortably in context (roughly a few hundred pages) | It does not fit, changes per user, or cost and latency from repeating it are too high even with prompt caching |
| Retrieval | The knowledge is too large or per-user | Measured retrieval quality is the bottleneck; then improve chunking, add keyword search alongside embeddings, or rerank |
| Workflow (fixed code path of model calls) | Steps are known in advance: chain with gates, route to handlers, run parts in parallel, or draft-then-critique | The steps genuinely cannot be known until runtime |
| Agent (model chooses tools in a loop) | Open-ended tasks where the path depends on what it finds, and the environment gives it ground truth | One agent's context or time cannot cover independent subtasks |
| Multiple agents | High-value tasks that split into independent parts, worth several times the tokens of one agent | — |

An agent needs a stopping condition (iteration, time, or cost cap) and a way to check
its own progress against the environment. Multiple agents cost many times more tokens
than one; they suit breadth-first work, not tasks whose parts depend on each other.

## Rules

- Validate structured output against its schema in code, even when the provider
  offers schema-constrained generation; treat malformed output as a handled failure.
- When the knowledge base may lack the answer, give the model and the code a way to
  say so, and return that as a distinct result rather than a fluent guess.
- The model may propose an action; application code decides whether it is allowed.
  Confirm irreversible or external actions with the user or a policy check.
- Bound everything that can grow: output tokens, context size, tool calls, loop
  iterations, retries, and tool response size.
- Log enough per request to debug a failure: the inputs, the model's raw output,
  tool calls and results, and the decision taken. Redact secrets and personal data.

## Gotchas

- A retrieved document, email, web page, or tool result can contain instructions.
  Content is never authority; a successful injection should be unable to reach a
  sensitive action.
- Wrapping every API endpoint as a tool makes agents worse. Fewer tools shaped
  around the user's tasks, with detailed descriptions, work better.
- Exact-match and LLM-judge evals both mislead when unchecked: grade outcomes in
  code where you can, and read a sample of transcripts and judge verdicts yourself.
- A cheaper model or lower effort setting is a cost lever worth testing before
  adding caching layers or routing infrastructure; let the eval decide.

## References

- `references/evaluation.md` — read when building the eval set or deciding whether a change helped.
- `references/tools.md` — read when defining tools the model can call or tuning their responses.
- `references/injection.md` — read when the model reads emails, documents, web pages, or any third-party content.
- `references/retrieval.md` — read when the knowledge does not fit in the prompt.
- `references/sources.md` — the published guidance this skill follows, with fetch dates and versions.
- `assets/agents-snippet.md` — copy into the project's agent instruction file for always-on defaults.
