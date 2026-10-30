# Static review rubric

Review a skill by reading it, before spending any agent runs. Run the repository
validator first if one exists; everything below is what a validator cannot judge.

Rate each finding **critical** (the skill will misfire or mislead), **major** (it
will underperform), or **minor** (polish). Report file and line for each.

## Description

- States what the skill does and when to use it; key use case in the first sentence,
  because some clients truncate descriptions.
- Third person ("Writes…", "Guides…"), with "Use when …" naming user intents, not
  internal mechanics. Covers indirect phrasings where the user never names the domain.
- States what it is not for when a neighboring skill or common request is close.
- No trigger-phrase dumps, no vendor or tool names, under 1024 characters.

## Body

- Every paragraph passes the test "would the agent get this wrong without it?".
  Background the agent already knows is a major finding.
- Gives defaults, not menus: one recommended path, alternatives as exceptions.
- Explains *why* behind rules; all-caps MUST/NEVER without a reason is minor.
- Gotchas live in `SKILL.md`, not only in references.
- Workflows that have an order use a checklist; fragile steps are exact commands.
- Output formats are given as templates.
- Under 500 lines; content needed only sometimes is in `references/` with a stated
  condition for reading it ("Read `references/x.md` when …").
- Vendor-neutral: no client-specific tool names, variables, or frontmatter; where a
  capability may be missing (sub-agents, network, a CLI), the text says what to do
  in both cases.
- Time-sensitive facts carry a "verified on" date or are fetched at run time.

## References and scripts

- One level deep from `SKILL.md`; every file is referenced and every reference exists.
- Files over 100 lines open with a short contents list.
- Scripts are non-interactive, have `--help`, print structured output, fail with
  actionable messages, and state their dependencies. `SKILL.md` says whether to run
  or read each one.

## Evals present

- `evals/evals.json` has at least three cases, varied phrasing, at least one edge case.
- `evals/trigger-queries.json` has 16–24 queries, roughly balanced, negatives are
  near-misses, sets are assigned.

## Report format

```markdown
## Static review: <skill-name>

Verdict: pass | needs work | major revision

| Severity | Location | Finding | Fix |
|---|---|---|---|
| critical | SKILL.md:3 | ... | ... |

Strengths: <one line>
```

Verdict is *major revision* with any critical finding, *needs work* with any major
finding, otherwise *pass*.
