# Tools and workflows

## Tool contract

A tool contract states:

- name and narrow purpose;
- typed, bounded arguments and validation rules;
- read vs. write side effect;
- authorization and confirmation requirement;
- idempotency/retry behavior;
- structured success and failure result.

Keep the application as the authority. The model can request a tool; ordinary code
checks whether it may run and whether the result is acceptable.

## Orchestration choice

- Direct call: one response or extraction.
- Chain: fixed sequence where each stage has a schema and a validation gate.
- Router: choose among a small set of known handlers; log the routing decision.
- Planner/executor: only when the steps cannot be known ahead of time; cap steps,
tools, budget, and depth.
- Human checkpoint: before irreversible, external, financial, privacy-sensitive, or
high-impact action.

Persist workflow state when a retry or restart must resume safely. Make duplicate
requests harmless where possible; otherwise require a confirmation or idempotency key.
