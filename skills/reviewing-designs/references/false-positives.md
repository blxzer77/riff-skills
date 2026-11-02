# Not design findings

Adapted from the false-positive lists in the code-review designs in `sources.md`
and the guidance that reviewers asked to find gaps over-report. Drop these unless
they cause a failure listed under "What to report".

- **Taste.** A different but valid pattern, layering, naming, or document layout.
  "I would use a repository class here" is not a finding.
- **Your favourite technology.** Recommending a queue, cache, framework, or
  library the design does not need. Adding a component is a cost, not a fix.
- **Speculative scale.** Load, team size, or traffic the project does not have and
  the design does not claim to target.
- **Reopening an accepted decision without a new fact.** A design that follows an
  accepted decision record is not wrong because you would have decided otherwise.
- **Accepted trade-offs.** A cost the design names and accepts with a reason
  (at-least-once delivery, state lost on restart) is a decision, not a gap.
- **Missing sections that change nothing.** No "security" heading on a change with
  no new input or data; no metrics plan for a weekly report.
- **Missing tests as such.** Report a test gap only when it hides a stated risk that
  the design depends on.
- **Pre-existing problems.** Something already wrong in the project that this design
  neither causes nor depends on. Mention it at most in one line after the findings.
- **Pedantry.** Wording, typos, formatting, diagram style.
