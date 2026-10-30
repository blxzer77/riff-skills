# Output evaluation

Contents: [Write cases](#write-cases) · [Run](#run) · [Assertions](#assertions) · [Grade and aggregate](#grade-and-aggregate) · [Review](#review) · [Iterate](#iterate)

Measures whether the skill makes the agent's work better than the same agent
without it (or than the previous version), and what that costs.

## Write cases

Store cases in `<skill>/evals/evals.json` (format: `references/schemas.md`).

- Start with three. Expand only after the first iteration shows what matters.
- Write prompts the way the user actually writes: file paths, backstory, casual
  phrasing in one, precise phrasing in another.
- Include one edge case: an ambiguous request, a case the skill should decline, or
  a situation where its default is wrong.
- Prefer tasks with checkable artifacts. For code skills, ship a small fixture
  project under `evals/files/` so the run produces a real diff.
- Test the behavior the skill exists to cause, in prompts that do not ask for it.
  A testing skill is best measured on "fix this bug" or "add this feature", where
  the baseline skips tests, not on "write tests for X", where any capable agent
  already does. Explicit requests mostly measure the base model.
- Write `expected_output` in prose. Leave `assertions` empty for now.

## Run

```bash
python3 scripts/run_evals.py --skill <skill-dir> --agent <agent> [--model <m>]
```

- Baseline is `without_skill` for a new skill. When revising, snapshot first
  (`cp -r <skill-dir> <workspace>/skill-snapshot`) and pass `--baseline old_skill`.
- Each run gets a fresh sandbox and a clean agent context; the user's global
  instructions and other skills must not load (see `references/agents.md`).
- Use `--runs 3` once assertions exist; single runs are for the first look.
- Evaluate with every agent and model the skill must serve; behavior differs.

Without a supported agent CLI, run each case yourself in a fresh session per
configuration, save the final response and diff into the same layout, and continue.

## Assertions

Write them after reading the first outputs, while the next runs execute.

- Checkable from artifacts: "the new test fails on the original code", "the ADR has
  a Consequences section naming at least one downside".
- Discriminating: it should be possible to fail. "The response mentions tests" is
  not; "the diff adds a test file exercising `apply_discount`" is.
- Mechanical checks belong in scripts under `evals/checks/` (exit 0 = pass). Use
  them for anything a program can decide: a test fails before and passes after,
  a file parses, a section exists.
- To check that tests the agent wrote are meaningful, run them against plausible
  wrong implementations (hand-written mutants) and require that they fail; to check
  a bug was reproduced, run the agent's tests against the original fixture.
- Check every check before trusting it: run it on the untouched fixture (must
  fail), on a hand-written good solution (must pass), and on a near-miss bad one
  (must fail).
- Process assertions ("ran the test and saw it fail before editing the code") are
  graded from the tool-call log the grader receives, not from the response's claims.
- Not everything needs an assertion. Style and judgment go to human review.

## Grade and aggregate

```bash
python3 scripts/grade.py --iteration <workspace>/iteration-N --skill <skill-dir> --agent <agent>
python3 scripts/aggregate.py --iteration <workspace>/iteration-N
```

The grader follows `references/grader.md`. Read its `eval_feedback`; weak assertions
are fixed before the next iteration, not after the skill "passes".

Then read `benchmark.md` with `references/analyzer.md` in mind:

| Pattern | Meaning | Action |
|---|---|---|
| pass in both | agent already does it | replace with a harder assertion or drop |
| fail in both | broken assertion or impossible task | fix before iterating |
| primary only | the skill's value | keep; note which instruction caused it |
| baseline only | the skill hurts | highest priority |
| high variance | ambiguity or flakiness | tighten wording, add an example |

Also compare `delta.tokens` and `delta.time_seconds` against `delta.pass_rate`.

## Review

Show the user each case: prompt, both outputs, grades. Record one line per case in
`feedback.json`; empty means no complaint. Specific beats general: "test mocks the
repository it is supposed to verify" is actionable, "tests are weak" is not.

For a holistic A/B judgment, use `references/comparator.md` with a reviewer that has
not seen the skill.

## Iterate

Revise using three signals together: failed assertions, human feedback, and
transcripts (they show *why*: ignored instructions, wasted steps, missed references).

- Generalize. The skill will see thousands of prompts; a patch for one case that
  reads like the eval prompt is overfitting.
- Remove before adding. If transcripts show wasted work, cut the instruction causing
  it. If pass rate plateaus while rules grow, the skill is over-constrained.
- Explain the reason behind each rule rather than escalating emphasis.
- If every run writes the same helper, bundle it into `scripts/`.

Rerun into `iteration-N+1`, always with the baseline. Stop when feedback is empty,
pass rate stops improving, or the remaining failures are outside the skill's control.
