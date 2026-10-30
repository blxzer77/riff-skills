---
name: reviewing-designs
description: Reviews architecture proposals, ADRs, RFCs, and implementation plans against the actual project, surfacing high-confidence risks in scope, tradeoffs, module boundaries, API evolution, tests, security, and operational fit. Use when the user asks for a design review, architecture review, ADR review, RFC review, or a sanity check before implementation, including when the design is only in chat. Not for reviewing a code diff; use reviewing-code.
license: Apache-2.0
metadata:
  verified-on: "2026-10-30"
---

# Reviewing designs

A design review should prevent expensive wrong turns, not reward elaborate diagrams.
Read the project before judging the proposal. Report concrete risks and missing
reasoning; do not replace the author's design with a second design unless asked.

## Workflow

- [ ] Identify the artifact, decision, review scope, and implementation stage. Ask
      one batched clarification when goals or constraints are missing; otherwise
      proceed with explicit assumptions.
- [ ] Read scoped project instructions, existing ADRs/design docs, manifests, and
      the code paths the proposal changes. Record conventions and facts with paths.
- [ ] Check problem, goals, non-goals, constraints, quality attributes, and success
      measures. A solution presented without a measurable problem is a warning.
- [ ] Check alternatives. Require at least one viable alternative and the reason it
      lost; do not accept a strawman or a popularity argument.
- [ ] Trace boundaries and flows: ownership, dependencies, data, failure paths,
      public contracts, migration, and rollback. Compare the boundary to project
      size and team ownership.
- [ ] Check tests and confirmation: what proves the design works, what catches
      regression, and what is intentionally not tested.
- [ ] Validate cross-cutting concerns proportionate to the change: security,
      privacy, failure handling, cost, operability, and upgrade/exit path.
- [ ] Separate findings from preferences. Validate each finding against the code or
      document; suppress uncertain, pre-existing, and purely stylistic comments.
- [ ] Give one recommendation: approve, approve with changes, or do not approve.
      Keep alternatives in the rationale, not as an undecided menu.

## Review lenses

| Lens | Ask |
|---|---|
| Problem | Does the design solve the stated problem rather than a fashionable one? |
| Scope | Are goals, non-goals, assumptions, and consequences explicit? |
| Fit | Is the complexity proportional to current project size and proven needs? |
| Boundaries | Can modules change, test, and deploy without accidental coupling? |
| Contracts | Can API/data contracts evolve compatibly and be rolled back? |
| Failure | What happens on timeout, duplicate, partial success, restart, or migration failure? |
| Verification | What test, metric, or invariant would falsify the design? |
| Exit | Can a sticky technology or boundary be replaced if assumptions change? |

## Finding standard

Report only findings with confidence at least 80/100. A finding needs:

1. **Location** — section, diagram node, or file:line.
2. **Claim** — what is wrong or missing.
3. **Impact** — the concrete failure, cost, or blocked change.
4. **Evidence** — project fact or proposal text.
5. **Recommendation** — the smallest corrective change.

Between two severities, use the lower one. Do not report grammar, a linter issue,
or a disagreement that has no user/project consequence.

## Output

```markdown
## Design review: <artifact>

### Verdict
<approve | approve with changes | do not approve>

### Summary
<one paragraph, including assumptions>

### Findings
1. **[High] <title>** — `<location>`
   - Impact: <concrete consequence>
   - Evidence: <quote or project path>
   - Recommendation: <smallest fix>

### Missing evidence
- <spike, test, migration rehearsal, or decision record needed>

### What is sound
- <specific strength>
```

“No blocking findings” is a valid result. Do not invent concerns to fill the report.

## Gotchas

- A design doc that is only an implementation manual and contains no decision or
  tradeoff should be shortened or turned into code.
- More layers do not make a small project safer. Ask what failure or change the layer
  prevents before approving it.
- A diagram can hide ownership and failure behavior. Trace one real request and one
  failure through it.
- If the proposal changes a costly-to-reverse choice, require an ADR rather than
  burying the rationale in an implementation plan.

## References

- `references/design-doc.md` — required sections and decision quality; read for a new proposal.
- `references/architecture-lenses.md` — detailed review questions; read when the design crosses boundaries.
- `references/finding-rubric.md` — confidence and severity calibration.
- `assets/agents-snippet.md` — always-on project design-review rule.
