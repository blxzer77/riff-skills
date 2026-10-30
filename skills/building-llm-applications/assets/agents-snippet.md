## LLM features

Before shipping an LLM-powered feature, define its task, failure cost, data boundary,
cost/latency budget, and eval set. Keep model/provider code behind an adapter; validate
structured output and tool arguments in application code. Do not let a model authorize
an irreversible action. Run regression evals for prompt, retrieval, tool-schema, and
model changes, and keep a rollback path.
