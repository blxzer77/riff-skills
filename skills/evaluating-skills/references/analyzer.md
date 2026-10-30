# Analyzer

Two uses: reading a benchmark, and explaining why one version beat another.

## Reading a benchmark

Input: `benchmark.json`, the per-run `grading.json` files, and transcripts.
Report observations only. Do not propose fixes in this pass, because mixing diagnosis
with prescription biases which patterns you notice.

Look for:

- **Non-discriminating assertions**: listed in `assertion_patterns.pass_both`. The
  agent does this without the skill; they inflate the with-skill pass rate.
- **Broken or too-hard assertions**: `fail_both`. Either the assertion is wrong, the
  task is impossible, or the grader cannot see the evidence.
- **Where the skill helps**: `primary_only`. Name the instruction in `SKILL.md` that
  most plausibly caused each one.
- **Where the skill hurts**: `baseline_only`. Treat these as the most urgent signal.
- **Variance**: the same eval passing in some runs and failing in others means the
  instructions are ambiguous or the eval is flaky.
- **Cost**: time and token outliers; read that run's transcript for wasted steps.

Output a short list of notes, each one sentence with the eval name and evidence.

## Explaining a comparison

Input: the comparator result, both skill versions, and both transcripts. Now unblind.

1. Score instruction-following for each run (1–10) and list concrete deviations.
2. Identify what in the winning skill caused the win: an instruction, an example, a
   script, a reference that was loaded at the right time.
3. Identify what in the losing skill caused the loss: ambiguity, missing guidance,
   a reference the agent never loaded, instructions it followed into a dead end.
4. Propose changes to the skill, not to the agent, each tagged
   `high | medium | low` and one of `instructions | examples | scripts | references |
   structure | description`. Prefer changes that generalize beyond this eval; flag any
   change that would only fix this one prompt.
