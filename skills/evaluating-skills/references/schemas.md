# Eval file schemas

Contents: [Authored files](#authored-files) · [Workspace layout](#workspace-layout) · [Per-run files](#per-run-files) · [Iteration files](#iteration-files) · [Trigger results](#trigger-results)

These formats follow the Agent Skills evaluation guides (agentskills.io) and stay
compatible with them: field names are identical where both define a field, and
extensions are additive. All scripts in `scripts/` read and write exactly these shapes.

## Authored files

Both files live in `<skill>/evals/` and are committed with the skill.

### evals.json

```json
{
  "skill_name": "writing-tests",
  "evals": [
    {
      "id": 1,
      "name": "regression-test-for-bug",
      "prompt": "Realistic user message, with paths and context.",
      "expected_output": "Human-readable description of success.",
      "files": ["evals/files/cart-service"],
      "assertions": [
        "The response names the behavior the new test protects",
        {
          "text": "The new test fails against the original code",
          "script": "evals/checks/fails_before_fix.py"
        }
      ]
    }
  ]
}
```

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Integer, unique within the file. |
| `name` | no | Kebab-case slug. Directory becomes `eval-<name>`; falls back to `eval-<id>`. |
| `prompt` | yes | What a real user would type. |
| `expected_output` | yes | Prose; guides graders and human reviewers. |
| `files` | no | Paths relative to the skill root. A file is copied into the run's working directory by basename; a directory has its *contents* copied into the working directory root. |
| `assertions` | no | Add after the first run. A string is graded by an LLM grader. An object with `script` is graded mechanically. |

**Script assertions.** The script runs with the run directory as its working
directory and these environment variables:

| Variable | Value |
|---|---|
| `EVAL_WORKDIR` | Final state of the agent's working directory (`outputs/workdir`) |
| `EVAL_FIXTURE` | Pristine copy of the eval's input files |
| `EVAL_RESPONSE` | Path to the agent's final message (`outputs/response.md`) |

Exit code 0 means PASS, anything else FAIL. The last 2,000 characters of stdout
and stderr become the evidence. Use any interpreter via a shebang.

### trigger-queries.json

```json
[
  {"query": "realistic prompt that should load the skill", "should_trigger": true, "set": "train"},
  {"query": "near-miss prompt that should not", "should_trigger": false, "set": "validation"}
]
```

`set` is `train` or `validation`; keep about 60/40, stratified by `should_trigger`,
and never move a query between sets once optimization starts.

## Workspace layout

The default workspace is `.workspace/<skill-name>/` under the current directory.
It must stay out of version control and outside any directory that agents scan
for skills, because `skill-snapshot/` contains a `SKILL.md`.

```
.workspace/<skill-name>/
├── skill-snapshot/                 # copy of the previous version (old_skill baseline)
├── iteration-1/
│   ├── run_config.json             # skill path, agent, model, configurations
│   ├── eval-<name>/
│   │   ├── eval_metadata.json
│   │   ├── with_skill/
│   │   │   └── run-1/              # one directory per repetition
│   │   │       ├── outputs/
│   │   │       │   ├── response.md     # final assistant message
│   │   │       │   ├── changes.patch   # working directory diff vs. fixture
│   │   │       │   ├── workdir/        # final working directory, skill install removed
│   │   │       │   ├── transcript.jsonl
│   │   │       │   └── agent-stderr.log  # only when the agent wrote to stderr
│   │   │       ├── timing.json
│   │   │       └── grading.json
│   │   └── without_skill/          # or old_skill/
│   ├── benchmark.json
│   ├── benchmark.md
│   └── feedback.json
└── triggers/
    └── <timestamp>-<set>.json
```

Each run executes in a fresh sandbox directory outside the repository (default
`~/.cache/riff-skills/runs/`), initialized as a git repository with the fixture
committed, so `changes.patch` is `git diff` against that commit. The skill is
installed where the agent discovers it, excluded from git, and removed before
`workdir/` is copied out.

### run_config.json

```json
{"skill_name": "writing-tests", "skill_dir": "/abs/path/skills/writing-tests",
 "snapshot_dir": null, "agent": "pi", "model": null,
 "configurations": ["with_skill", "without_skill"], "runs": 1,
 "created": "2026-10-30T09:00:00Z"}
```

`configurations` is the subset actually run (`run_evals.py --configs`).

## Per-run files

### eval_metadata.json

```json
{"id": 1, "name": "regression-test-for-bug", "prompt": "...", "expected_output": "...", "assertions": ["..."]}
```

### timing.json

```json
{"total_tokens": 84852, "duration_ms": 23332, "agent": "pi", "model": "provider/model", "exit_code": 0}
```

`total_tokens` is `null` when the agent does not report usage. Duration is measured
by the runner around the agent process, never taken from the agent's own report.
A run killed by `--timeout` adds `"timed_out": true`. A run whose agent ended in an
error state after all retries adds `"error": "<message>"`; it is not graded and is
excluded from the benchmark (counted as `errored_runs` per configuration). Token accounting differs per
agent (some include cache reads), so compare tokens within one agent only.

### grading.json

```json
{
  "assertion_results": [
    {"text": "...", "passed": true, "evidence": "Quoted from response.md: ...", "method": "llm"},
    {"text": "...", "passed": false, "evidence": "pytest: 3 passed", "method": "script"}
  ],
  "summary": {"passed": 1, "failed": 1, "total": 2, "pass_rate": 0.5},
  "claims": [{"claim": "...", "type": "factual", "verified": false, "evidence": "..."}],
  "eval_feedback": {"suggestions": [{"assertion": "...", "reason": "..."}], "overall": "..."}
}
```

`claims` and `eval_feedback` are optional and come from the LLM grader.

## Iteration files

### benchmark.json

```json
{
  "metadata": {"skill_name": "writing-tests", "iteration": 1, "agent": "pi", "model": "...",
               "primary": "with_skill", "baseline": "without_skill", "timestamp": "..."},
  "evals": [
    {"name": "regression-test-for-bug",
     "with_skill": {"pass_rate": 1.0, "time_seconds": 41.2, "tokens": 30211, "runs": 1},
     "without_skill": {"pass_rate": 0.33, "time_seconds": 30.5, "tokens": 18003, "runs": 1}}
  ],
  "run_summary": {
    "with_skill": {"pass_rate": {"mean": 0.83, "stddev": 0.06},
                   "time_seconds": {"mean": 45.0, "stddev": 12.0},
                   "tokens": {"mean": 3800, "stddev": 400}},
    "without_skill": {"pass_rate": {"mean": 0.33, "stddev": 0.10},
                      "time_seconds": {"mean": 32.0, "stddev": 8.0},
                      "tokens": {"mean": 2100, "stddev": 300}},
    "delta": {"pass_rate": 0.50, "time_seconds": 13.0, "tokens": 1700}
  },
  "assertion_patterns": {
    "pass_both": [], "fail_both": [], "primary_only": [], "baseline_only": []
  }
}
```

`delta` is always primary minus baseline. `assertion_patterns` lists
`"<eval-name>: <assertion text>"` entries; `pass_both` and `fail_both` are the
candidates to replace (see the output evaluation guide).

### feedback.json

```json
{"eval-regression-test-for-bug": "Test asserts on a private helper instead of the public API.",
 "eval-flaky-test-diagnosis": ""}
```

Empty string means the reviewer had no complaint.

## Trigger results

```json
{
  "skill_name": "writing-tests",
  "description": "the description that was tested",
  "agent": "pi", "model": "...", "set": "train",
  "runs_per_query": 3, "threshold": 0.5,
  "results": [
    {"query": "...", "should_trigger": true, "set": "train",
     "triggers": 2, "runs": 3, "trigger_rate": 0.67, "passed": true}
  ],
  "summary": {"total": 12, "passed": 10, "failed": 2,
              "false_negatives": 1, "false_positives": 1}
}
```

A query passes when `trigger_rate >= threshold` for `should_trigger: true`, and
`trigger_rate < threshold` for `should_trigger: false`. When every run of a query
failed (agent error or timeout), `passed` is `null` and the query is counted in
`summary.errored` instead of as a false result. Files are named
`<UTC %Y%m%dT%H%M%S%fZ>-<set>.json`.
