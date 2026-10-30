# riff-skills

Agent Skills for software engineering work that agents tend to skip or get wrong:
writing tests, recording decisions, choosing technologies, drawing module and API
boundaries, reviewing code and designs, and building LLM applications.

Every skill follows the open [Agent Skills specification](https://agentskills.io/specification)
and uses only its standard frontmatter, so the same directory works in any compliant
agent.

## Skills

| Skill | Use it to |
|---|---|
| [authoring-skills](skills/authoring-skills) | Write or restructure a skill that works across agents |
| [evaluating-skills](skills/evaluating-skills) | Review, benchmark, and tune the triggering of a skill |
| [selecting-technologies](skills/selecting-technologies) | Choose stable, proportionate technologies with current evidence |
| [designing-modules](skills/designing-modules) | Set module boundaries proportional to project size |
| [designing-apis](skills/designing-apis) | Design maintainable, evolvable API contracts |
| [writing-tests](skills/writing-tests) | Write tests that catch regressions and repair flaky suites |
| [writing-adrs](skills/writing-adrs) | Record significant decisions and their tradeoffs |
| [reviewing-code](skills/reviewing-code) | Review diffs with evidence and false-positive control |
| [reviewing-designs](skills/reviewing-designs) | Review architecture proposals against the actual project |
| [building-llm-applications](skills/building-llm-applications) | Build reliable, evaluated, cost-bounded LLM features |

## Install

Copy or symlink a skill directory into a location your agent scans:

| Agent | Project | User |
|---|---|---|
| Codex, Cursor, Gemini CLI, OpenCode, Pi, and others | `.agents/skills/` | `~/.agents/skills/` |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |

Or install with the [`skills`](https://github.com/vercel-labs/skills) CLI:

```bash
npx skills add blxzer77/riff-skills                 # choose skills and agents interactively
npx skills add blxzer77/riff-skills --skill writing-tests
```

Claude Code can also add this repository as a plugin marketplace:

```
/plugin marketplace add blxzer77/riff-skills
/plugin install riff-skills@riff-skills
```

## Habits that must always hold

A skill only acts while it is loaded. For behavior that should hold in every session,
such as adding a regression test with every bug fix, paste the skill's `AGENTS.md`
snippet (where provided) into your project's `AGENTS.md`.

## Contributing

Read [AGENTS.md](AGENTS.md). In short: start from `template/`, follow
`skills/authoring-skills`, ship evals, and run `python3 scripts/validate.py --strict`
before listing a skill. Use `skills/evaluating-skills` to run behavioral benchmarks
before calling a skill production-ready; the first behavioral benchmarks in this repo
are recorded for `writing-tests` and `writing-adrs`.

## License

Apache-2.0. See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
