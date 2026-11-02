# Verifying a design finding

Adapted from the refute-first verifier designs listed in `sources.md`.

Each candidate gets one job: try to disprove it. Report it only if that fails.

## The standard

A design finding has two sides. Keep it only when you can cite both:

1. **The design's claim or step** — the section and sentence of the proposal (or
   what was said in chat).
2. **The project fact it collides with** — a file and line: a process or scheduler
   config, a route that exposes a field, a caller outside the stated scope, an
   accepted decision record, a schema.

Then state the consequence in this project: what fails, for whom, and when. "This
might not scale", "consider event sourcing", or "best practice says" has no second
side and is not a finding.

## Try to disprove it

- Search the proposal for the section that already handles it (a rollback step, a
  stated non-goal, an accepted trade-off). An accepted trade-off with a reason is
  a decision, not a defect.
- Search the project for the guard that makes it safe: a lock, a uniqueness
  constraint, a version prefix, an existing adapter.
- Check that the decision record you cite is accepted and not superseded.

Do not invent a defense to drop a finding either. Drop it only for a mitigation you
found and read.

## Confidence and severity

Report a finding when you are confident (about 80 out of 100 or higher) that both
sides hold and the consequence follows. Below that, drop it or ask one question in
the summary. Severity follows the consequence the evidence supports. Lower it when
verification shows a hurdle; never raise it to make a point.

## Independence

The person who found a candidate is its worst verifier. When independent workers
are available, give each candidate to a fresh one with the claim and repository
access but not the reasoning behind it. Otherwise re-read the cited lines from
scratch before keeping it.
