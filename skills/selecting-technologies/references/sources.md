# Sources

Anthropic and the Claude Code team have not published a technology-selection or
dependency-evaluation method. What they have published, and this skill follows, is
four principles that bear directly on it. The concrete evaluation criteria come
from the non-Anthropic primary sources further down. All pages were fetched on
2026-11-02.

## Anthropic / Claude Code

| Source | What this skill takes from it |
|---|---|
| `anthropics/claude-plugins-official` `a7ba5b9`, `plugins/feature-dev` (commands/feature-dev.md, agents/code-architect.md) | Read existing patterns and the technology stack before deciding; follow codebase conventions; for "whatever you think is best", recommend and get confirmation |
| Same repository, `plugins/agent-sdk-dev/commands/new-sdk-app.md` | Check the latest package versions and version requirements from npm/PyPI and official docs before installing; tell the user what was chosen |
| Same repository, `plugins/mcp-server-dev/skills/build-mcp-server/references/versions.md` | Keep dated facts in a "last verified" ledger with a command to re-check them |
| Same repository, `plugins/code-modernization/agents/architecture-critic.md` | Skeptical default toward the new and shiny: "do we actually need this?"; simplest design that meets the requirements; the migration story is part of the decision |
| Building effective agents (2024-12-19) | Find the simplest solution and increase complexity only when needed |
| Claude Code best practices | Read the code to learn layout and conventions; record decisions that are not in the repository |
| Prompting best practices | Do not over-engineer or design for hypothetical requirements; read files before answering about them |
| Models overview, model IDs and versions, model deprecations | Model IDs are pinned snapshots with published retirement dates; check the current lists |

## Non-Anthropic primary sources

| Source | What this skill takes from it |
|---|---|
| OpenSSF, Concise Guide for Evaluating Open Source Software (`ossf/wg-best-practices-os-developers` `b8ea05a`) | Consider necessity; verify authenticity and name (typosquatting); release and activity within 12 months; version stability; known vulnerabilities; avoid hype-driven choices; try the dependency in isolation |
| OpenSSF Scorecard, Maintained check (`ossf/scorecard` `2ef237f`) | Archived projects score lowest; lack of maintenance is a reason to investigate, not always a defect |
| Node.js previous releases and `nodejs/Release` schedule.json (`c3e8696`) | Production should use only Active or Maintenance LTS releases |
| endoflife.date API v1 | Machine-readable end-of-life dates; gate on `isEol`, not `isMaintained` |
| OSV.dev `POST /v1/query` | Cross-ecosystem vulnerability lookup by package and version |
| Dan McKinley, Choose Boring Technology (2015) | Each new technology has a lasting cost; first ask how to solve the problem with nothing new |
| Thoughtworks Technology Radar FAQ | Adopt / Trial / Assess / Caution: maturity is judged in context |

URLs:

- https://github.com/anthropics/claude-plugins-official
- https://www.anthropic.com/research/building-effective-agents
- https://code.claude.com/docs/en/best-practices
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- https://platform.claude.com/docs/en/models/overview
- https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions
- https://platform.claude.com/docs/en/about-claude/model-deprecations
- https://best.openssf.org/Concise-Guide-for-Evaluating-Open-Source-Software
- https://github.com/ossf/scorecard/blob/main/docs/checks.md
- https://nodejs.org/en/about/previous-releases
- https://raw.githubusercontent.com/nodejs/Release/main/schedule.json
- https://endoflife.date/docs/api/v1/
- https://google.github.io/osv.dev/post-v1-query/
- https://mcfunley.com/choose-boring-technology
- https://www.thoughtworks.com/radar/faq
