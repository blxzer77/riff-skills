# Investigating technology trends

A trend is relevant only when it changes the decision for this project.

## Process

1. State the claimed advantage in one sentence: lower latency, simpler operations,
   better developer experience, a new capability, or a changing ecosystem.
2. Check whether the advantage exists in the project's workload and constraints.
3. Find evidence from the project's official docs, release history, and at least one
   independent production report when available.
4. Identify what is still unknown: upgrade stability, tooling, security response,
   cost at scale, data migration, or long-term maintenance.
5. Run a small spike behind an adapter if the unknown can change the decision.
6. Revisit only when the trigger condition occurs; do not add a new dependency merely
   to keep the stack fashionable.

## Trend report

```markdown
Claim: <what changed>
Relevant to this project because: <specific requirement>
Verified: <sources and YYYY-MM-DD>
Unknown: <what evidence does not establish>
Decision impact: <none | shortlist | spike | choose>
Revisit when: <measurable trigger>
```
