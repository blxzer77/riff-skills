---
name: evaluating-skills
description: Evaluates Agent Skills with a static review, trigger tests, and with-versus-without output benchmarks graded on evidence, then improves the skill or its description from the results. Use when the user wants to test, benchmark, review, compare versions of, or tune the triggering of a skill, or asks whether a skill actually helps. Not for writing a new skill from scratch; that is authoring-skills.
license: Apache-2.0
---

# Evaluating skills

A skill is worth keeping only if an agent with it does measurably better work than
the same agent without it, and loads it when it should. Evaluate in four layers,
cheapest first, and stop at the layer that answers the user's question.

| Layer | Answers | Cost | Guide |
|---|---|---|---|
| 1. Static review | Is it well-formed and well-written? | no agent runs | `references/static-review.md` |
| 2. Trigger evals | Does the agent load it at the right times? | ~60 short runs | `references/trigger-evals.md` |
| 3. Output evals | Does it improve results, at what cost? | 2 × cases × runs | `references/output-evals.md` |
| 4. Comparison | Which of two versions is better overall? | reviewer passes | `references/comparator.md` |

Default when the user just says "evaluate this skill": layer 1, then layer 3 with a
`without_skill` baseline (or `old_skill` if a previous version exists), then layer 2.

## Workflow

- [ ] Read the skill: `SKILL.md`, its references, and `evals/` if present.
- [ ] Layer 1: run the repository validator if there is one, then review against
      `references/static-review.md`. Fix critical findings before spending runs.
- [ ] Pick the agent(s) and model(s) the skill must serve. Read
      `references/agents.md` for the supported adapters and isolation caveats.
- [ ] Ensure `evals/evals.json` exists (≥ 3 cases). Draft missing cases with the user;
      their real tasks make better cases than invented ones.
- [ ] Layer 3: run, grade, aggregate, review with the user, iterate.
- [ ] Layer 2: ensure `evals/trigger-queries.json` exists, measure, optimize if
      needed.
- [ ] Report (template below). Leave the workspace for the user; it is not committed.

## Scripts

All scripts are Python 3.11+ standard library; run them, don't read them. Each takes
`--help`. File formats are in `references/schemas.md`.

| Script | Purpose |
|---|---|
| `scripts/run_evals.py` | Run every case with and without the skill in fresh sandboxes |
| `scripts/grade.py` | Grade runs: assertion scripts mechanically, the rest with an LLM grader |
| `scripts/aggregate.py` | Write `benchmark.json` / `benchmark.md` with deltas and assertion patterns |
| `scripts/run_triggers.py` | Measure trigger rates for a query set or a candidate description |
| `scripts/split_queries.py` | Assign a fixed, stratified train/validation split |

Workspaces default to `.workspace/<skill-name>/` in the current directory. Keep that
path out of version control and away from any directory agents scan for skills.

## Without the scripts

When no supported agent CLI is available, follow the same layout by hand: for each
case, run the prompt in a fresh session with the skill and in another without it,
save the final response and resulting diff under
`iteration-N/eval-<name>/<config>/run-1/outputs/`, then grade with
`references/grader.md`. If sub-agents are available, use one per run so contexts
stay clean; otherwise use separate sessions. Never grade a run in the same context
that produced it.

## Gotchas

- Global instructions leak into runs. A user-level `AGENTS.md`/`CLAUDE.md` or
  globally installed skills change results; the adapters disable them, and manual
  runs must too.
- Agents skip skills for simple one-step requests. A trigger miss on a trivial query
  says nothing about the description.
- An assertion that passes in both configurations measures the agent, not the skill.
  A high with-skill pass rate built on such assertions is meaningless.
- The grader's verdict rests on artifacts. If the response claims work the diff does
  not show, that is a failure, not a pass on the strength of the claim.
- Compare cost with benefit: a skill that adds 2 points of pass rate for double the
  tokens may be worse than no skill.
- Results from one agent or model do not transfer. Report which ones were tested.
- A failed LLM grading is not a failed run. Before acting on a low score, read the
  evidence; "grader output unparseable" means re-grade, not revise the skill.
- When a run with the skill scores lower, read its output before blaming the skill.
  Often the cause is narrow, such as a bundled template the agent applied over the
  project's own conventions, and the fix is one rule with its reason.

## Report

```markdown
## Evaluation: <skill-name> (<agent>, <model>, iteration N)

Static review: pass | needs work | major revision — <top finding>
Output evals: <primary> <pass%> vs <baseline> <pass%> (Δ <+x pts>), Δ tokens <+n>, Δ time <+s>
Triggering: train <a/b>, validation <c/d>; false triggers: <list or none>

Where the skill helps: <assertion patterns, with the instruction responsible>
Where it hurts or is flat: <...>
Next changes: <ranked, each tied to evidence>
Not tested: <agents/models/cases not covered>
```
