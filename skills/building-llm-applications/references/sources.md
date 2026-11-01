# Sources

This skill adapts published guidance from Anthropic and the Claude team. It keeps the
principles and leaves out provider-specific API fields and model names, which change.
Pages were fetched on 2026-11-01; engineering posts and docs pages carry no version,
so check them for updates before relying on details.

| Source | What this skill takes from it |
|---|---|
| Building effective agents (anthropic.com/engineering) | Simplest solution first, possibly no agentic system; single call with retrieval and examples is often enough; workflows vs agents; chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer; stopping conditions; use APIs before frameworks; tool interface design |
| Writing effective tools for agents (anthropic.com/engineering) | Task-shaped tools over endpoint wrappers; consolidation and namespacing; high-signal responses without low-level identifiers; pagination, truncation, and concise formats; actionable errors; evaluating tools with realistic tasks |
| Effective context engineering for AI agents (anthropic.com/engineering) | Smallest high-signal context; overlapping toolsets as a failure mode; canonical examples over exhaustive rule lists |
| Contextual retrieval (anthropic.com/news) | Put a knowledge base under about 200,000 tokens in the prompt; keyword plus embedding search; contextual chunks and reranking reduce retrieval failures; tune chunk count with evals |
| How we built our multi-agent research system (anthropic.com/engineering) | Agents use about 4x and multi-agent systems about 15x the tokens of chat; multi-agent suits high-value breadth-first tasks, not tightly coupled ones; scale effort to the query |
| Demystifying evals for AI agents (anthropic.com/engineering) | 20–50 tasks from real failures to start; unambiguous tasks two experts agree on; balanced should/should-not sets; isolated trials; grade outcomes not paths; calibrate model graders and allow "unknown"; read transcripts |
| Docs: define success criteria; build evaluations | Measurable criteria; code graders before model graders before humans |
| Docs: reduce hallucinations | Allow the model to say it does not know; ground answers in quoted sources |
| Docs: mitigate jailbreaks and prompt injections | Direct vs indirect injection; keep untrusted content out of the instruction channel; label its source; structured encoding; least privilege; screening |
| Docs: tool use (define tools, implement tool use) | Detailed descriptions are the most important factor, at least three to four sentences; consolidate with an action parameter; meaningful names |
| Docs: prompt caching, reduce latency, choose a model | Caching for repeated context; smaller models, effort settings, output limits, and streaming as cost and latency levers |
| `anthropics/claude-cookbooks` @ `c43f56d` | Reference implementations of the workflow patterns; evaluating retrieval separately from end-to-end answers |

URLs:

- https://www.anthropic.com/engineering/building-effective-agents
- https://www.anthropic.com/engineering/writing-tools-for-agents
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- https://www.anthropic.com/news/contextual-retrieval
- https://www.anthropic.com/engineering/multi-agent-research-system
- https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- https://platform.claude.com/docs/en/build-with-claude/
- https://github.com/anthropics/claude-cookbooks
