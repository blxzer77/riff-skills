---
name: authoring-skills
description: Creates and revises Agent Skills that work across agent clients, from scoping and frontmatter through body structure, references, scripts, and eval cases. Use when the user wants to write a new skill, turn a workflow or recurring correction into a skill, restructure or shorten an existing skill, or fix a description that is not triggering. Not for measuring an existing skill; that is evaluating-skills.
license: Apache-2.0
---

# Authoring skills

A skill is a directory with a `SKILL.md`: YAML frontmatter that every agent reads at
startup, and a body the agent reads only after deciding the skill applies. Write for
any agent that implements the Agent Skills specification, not for one client.

## Workflow

- [ ] **Scope.** Name the behavior the skill must change and how you will know it
      changed. Find evidence the agent gets it wrong today: a transcript, a
      correction the user keeps making, a failing case. No evidence, no skill.
- [ ] **Gather material.** Real artifacts beat general knowledge: the user's
      corrections, project conventions, failure cases, primary sources. Content the
      agent already knows is cost without benefit.
- [ ] **Write eval cases first.** Three realistic prompts in `evals/evals.json` and a
      draft `evals/trigger-queries.json` (see the evaluating-skills skill). They keep
      the draft honest.
- [ ] **Draft** using `assets/SKILL.template.md` and the rules below.
- [ ] **Validate** with the repository validator, if present, and fix every error.
- [ ] **Evaluate** with the evaluating-skills skill; revise from evidence.

## Frontmatter

Use only fields defined by the Agent Skills specification so every client loads the
skill. Client-specific extensions (invocation control, tool grants, model overrides)
make a skill fail validation or behave differently elsewhere.

```yaml
---
name: designing-apis            # = directory name; lowercase, digits, single hyphens; ≤ 64
description: <see below>        # ≤ 1024 characters, no angle brackets
license: Apache-2.0             # optional
compatibility: Requires git.    # optional, only for real environment requirements
metadata:                       # optional, string values only
  verified-on: "2026-10-30"
---
```

Name with a gerund phrase for the activity (`writing-tests`, `reviewing-code`).
Avoid vague names (`helpers`, `utils`) and vendor names.

## Description

The description is the only text an agent sees when choosing among many skills.

```
<What it does, third person, key use case first>. Use when <user intents and
situations, including ones where the user never names the domain>. Not for
<nearest neighboring request or skill>.
```

- Lead with the main use case; some clients truncate long descriptions.
- Describe intents and situations, not internal mechanics or file formats.
- Be explicit about indirect triggers ("…or when a bug fix is about to ship
  without a test"). Agents under-load skills more often than they over-load them.
- Do not list eval queries or keyword dumps; generalize to the category.

## Body

- **Assume a capable agent.** For each paragraph ask: would the agent get this wrong
  without it? Cut what it already knows.
- **Defaults, not menus.** Recommend one approach; mention alternatives as
  exceptions with their condition.
- **Explain why.** A rule with its reason transfers to cases the rule did not
  foresee; shouted MUST/NEVER does not.
- **Match prescriptiveness to fragility.** Judgment tasks get criteria; fragile
  operations get exact commands.
- **Gotchas in `SKILL.md`.** Non-obvious facts the agent would get wrong belong
  where it reads them before acting. Add each correction you make during evals.
- **Templates for outputs.** Show the exact shape; agents copy structure reliably.
- **Checklists for ordered workflows,** validation loops for fragile ones.
- **Under 500 lines.** Move conditional detail to `references/` and say when to read
  each file: "Read references/pagination.md when designing list endpoints."
- **Vendor-neutral wording.** Say "ask the user", "read the file", "run". Where a
  capability may be missing, cover both: "If sub-agents are available, review each
  pass in a fresh one; otherwise run the passes sequentially." No client tool names,
  environment variables, or slash commands.
- **Dates on facts that age.** Anything about versions, prices, or "current"
  practice carries a verified-on date, or the skill tells the agent how to check.

## Files

```
<name>/
├── SKILL.md
├── references/   # read on demand; one level deep; contents list if > 100 lines
├── scripts/      # executed, not read; --help, structured output, clear errors
├── assets/       # templates and files copied into outputs
└── evals/        # evals.json, trigger-queries.json, files/, checks/
```

- Reference files from `SKILL.md` with relative paths; never chain references
  (a reference pointing to another reference gets partially read).
- Scripts state their dependencies, never prompt interactively, and say in
  `SKILL.md` whether to run or read them.
- Bundle a script when evals show the agent rewriting the same logic every run.

## Gotchas

- A `name` that differs from its directory loads in some clients and fails in others.
- Frontmatter parsers differ. Quote values containing `: ` and avoid flow-style
  lists (`[a, b]`); strict YAML parsers reject them.
- Two skills with overlapping descriptions compete; whichever an agent picks, the
  other silently stops working. Add "Not for …" on both sides.
- A skill that tells the agent to "always" do something only works while it is
  loaded. Habits that must hold in every session belong in the project's
  `AGENTS.md`; a skill can ship the snippet to paste there.
