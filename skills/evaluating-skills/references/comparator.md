# Blind comparator

Use when two configurations both pass their assertions but you need to know which
output is better overall, or when assertions cannot capture quality. Give a reviewer
in a fresh context only: the eval prompt, output **A**, output **B**, and optionally
the assertions. Randomize which configuration is A. Do not reveal which skill version
produced which output; record the mapping separately.

## Instructions for the reviewer

1. Read the task and decide what a good output must achieve.
2. Build a rubric with two dimensions, adapted to the task:
   - **Content**: correctness, completeness, accuracy.
   - **Structure**: organization, formatting, usability.
   Score each criterion 1–5 for A and for B.
3. Check assertions against both outputs if provided. They are secondary evidence.
4. Pick a winner by overall rubric score, then assertion pass rate. Ties should be
   rare; if both fail, pick the one that fails less badly.
5. Stay blind. Do not guess which version produced which output.

## Output

```json
{
  "winner": "A",
  "reasoning": "Specific differences that decided it.",
  "rubric": {
    "A": {"content": {"correctness": 5, "completeness": 4, "accuracy": 5},
          "structure": {"organization": 4, "formatting": 4, "usability": 5},
          "content_score": 4.7, "structure_score": 4.3, "overall_score": 9.0},
    "B": {"content": {"correctness": 3, "completeness": 2, "accuracy": 3},
          "structure": {"organization": 3, "formatting": 3, "usability": 3},
          "content_score": 2.7, "structure_score": 3.0, "overall_score": 5.7}
  },
  "strengths": {"A": ["..."], "B": ["..."]},
  "weaknesses": {"A": ["..."], "B": ["..."]}
}
```

`content_score` and `structure_score` are criterion means (1–5);
`overall_score` is their sum (2–10). Save as `comparison-<eval-name>.json` in the
iteration directory together with the A/B mapping.
