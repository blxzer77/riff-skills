# Third-party notices

## SDFrame (Caldis/frameworks)

Source: https://github.com/Caldis/frameworks, commit
`e519d0dd4d16be63b956fd35ab52fd6644840328`.

Used as source material only: topic selection and reading lists for skill references.
Skill content in this repository is rewritten and checked against the primary
sources it cites; no upstream text is reproduced verbatim. The mapping from upstream
entries to skills, and the reason each excluded entry was cut, is in
`sources/sdframe.yaml`.

The upstream README states the MIT License; at the pinned commit the repository
contains no LICENSE file.

## Agent Skills evaluation method

The evaluation workflow, file formats, and grader/comparator/analyzer roles in
`skills/evaluating-skills/` are adapted from the Agent Skills documentation
(https://agentskills.io) and Anthropic's `skill-creator` skill
(https://github.com/anthropics/skills, Apache-2.0). Changes: vendor-neutral agent
adapters, per-run sandboxes, unified field names, baseline-relative deltas, and
rewritten role prompts.
