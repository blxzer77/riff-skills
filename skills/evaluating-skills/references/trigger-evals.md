# Trigger evaluation and description optimization

Agents see only `name` and `description` until they decide to load a skill, so the
description alone decides whether the skill is ever used.

## Write the query set

Store it in `<skill>/evals/trigger-queries.json` (format: `references/schemas.md`).

- About 20 queries: 8–12 should trigger, 8–12 should not.
- Should-trigger queries vary phrasing (casual, terse, with typos), explicitness
  (names the domain vs. only describes the need), and detail. The most valuable ones
  need the skill without saying so: "this checkout bug came back again, fix it" for
  a testing skill.
- Should-not-trigger queries are near-misses that share vocabulary but need something
  else: "run the test suite and tell me what fails" for a skill about writing tests.
  "Write a fibonacci function" tests nothing.
- Make every query substantive. Agents skip skills for one-step tasks they can do
  alone, so a trivial query that fails to trigger tells you nothing about the
  description.
- Assign sets once: `python3 scripts/split_queries.py <file>` (60/40, stratified).

## Measure

```bash
python3 scripts/run_triggers.py --skill <skill-dir> --agent <agent> --set all --runs 3
```

A query's trigger rate is the fraction of runs in which the agent loaded the skill.
Should-trigger passes at ≥ 0.5; should-not-trigger passes below 0.5. Run against
every agent the skill must serve; they weigh descriptions differently.

## Optimize

1. Run on `train` and `validation`.
2. Look only at **train** failures. Never let validation queries or their results
   into the revision; that turns validation into training data.
3. Revise toward the category the failures represent, not their words:
   - Missed triggers: the description is too narrow or names mechanics instead of
     user intents. Add the situation, not the phrase.
   - False triggers: it is too broad. State what the skill does not do, or where a
     neighboring skill takes over.
   - Stuck after two rounds: try a structurally different description.
4. Test a candidate without editing the skill:
   `run_triggers.py --description-file candidate.txt --set train`.
5. Stop after about five rounds or when train passes fully. Pick the round with the
   best **validation** pass rate; it is often not the last one.
6. Confirm with 5–10 fresh queries written after optimization ended.

If nothing improves, suspect the queries (mislabeled, too easy, too hard) before the
description. Keep the final description under 1024 characters and free of queries
copied from the eval set.
