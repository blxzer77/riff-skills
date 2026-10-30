---
name: selecting-technologies
description: Makes evidence-based technology choices that fit a project's size, structure, constraints, and likely evolution, while separating stable defaults from genuinely useful new technology. Use when choosing or replacing a language, framework, library, datastore, hosting platform, model provider, or major infrastructure dependency, or when a project is drifting toward a popular option without a written comparison. Not for choosing a tiny implementation dependency already constrained by project conventions.
license: Apache-2.0
metadata:
  verified-on: "2026-10-30"
---

# Selecting technologies

Choose the smallest mature option that meets the real requirements and leaves a
reversible path. A new technology is not valuable because it is new; it is valuable
when its advantage matters to this project and outweighs its adoption and lock-in
cost.

## Workflow

- [ ] **Inspect the project.** Read the package manifests, build/deploy files,
      existing ADRs, project instructions, and neighboring implementations. Record
      the current stack, team familiarity, deployment shape, and constraints before
      naming candidates.
- [ ] **Define the decision.** Write the capability being chosen, the decision date,
      the must-haves, nice-to-haves, non-goals, and the cost of being wrong. Separate
      a reversible library choice from a sticky datastore, language, hosted service,
      or public protocol.
- [ ] **Shortlist 2–4 real candidates.** Include the current choice or a no-change
      option when it is viable. Remove candidates that fail a must-have before
      scoring; do not use a weighted table to rescue them.
- [ ] **Verify current facts.** Check official documentation, release activity,
      supported runtimes, license, security advisories, migration path, and ecosystem
      evidence on the day of the decision. Record URLs and the date checked. Do not
      present model memory as a current trend.
- [ ] **Compare fit and cost.** Use the scorecard in `references/scorecard.md`; use
      qualitative High/Medium/Low unless measurements justify numbers. State unknowns
      rather than inventing precision.
- [ ] **Recommend one path.** Explain why it fits this project's size and structure,
      what it gives up, confidence level, and the first low-cost validation step. If
      evidence is insufficient, recommend a time-boxed spike, not a permanent
      dependency.
- [ ] **Record sticky choices.** Use `writing-adrs` when the choice is costly to
      reverse, changes boundaries, or introduces a hosted dependency. Include the
      rejected alternatives and the evidence behind the choice.

## Decision defaults

| Situation | Default | Escape hatch |
|---|---|---|
| Small project, ordinary web/API capability | Existing language/framework and a boring library | A measured limitation blocks the product or maintenance |
| New project with unclear boundaries | One deployable with explicit internal modules | Independent scaling, ownership, or release needs are already proven |
| New datastore | Existing datastore if it fits the access patterns | A concrete query, consistency, scale, or operational requirement fails |
| Emerging technology | Spike behind a replaceable boundary | It has production evidence relevant to this project and the failure cost is acceptable |
| Hosted dependency | Keep the integration behind a port and define an exit path | The service is the product requirement and portability is not valuable |

## Output

```markdown
## Technology decision: <capability>

### Recommendation
<one choice and confidence: high / medium / low>

### Project fit
<current structure, scale, constraints, and why this choice fits>

### Alternatives rejected
- <candidate>: <specific reason>

### Risks and exit path
- <adoption, lock-in, operational, security, or migration risk>

### Evidence checked
- <source> — <fact> (checked YYYY-MM-DD)

### Validation step
<small spike, benchmark, or integration check with a pass/fail criterion>
```

## Gotchas

- Popularity is not evidence of fit. A technology's adoption outside the project's
  workload does not prove its operational or migration cost here.
- "Latest" is a query, not a property in the model's memory. Check current sources
  and state the check date; if network access is unavailable, mark the fact unknown.
- A benchmark without the project's workload is a story, not a decision. Prefer a
  small representative spike over a generic leaderboard.
- Do not compare a mature option with an emerging one using made-up equal scores.
  Explain evidence quality and uncertainty separately from fit.
- A choice that changes a public API, data format, module boundary, or deployment
  model is an ADR even if the implementation looks small.

## References

- `references/scorecard.md` — criteria and evidence table; read before comparing candidates.
- `references/evidence.md` — what to verify for maturity, maintenance, security, and lock-in.
- `references/trends.md` — how to investigate new technology without chasing novelty.
- `assets/agents-snippet.md` — always-on project rule for significant technology choices.
