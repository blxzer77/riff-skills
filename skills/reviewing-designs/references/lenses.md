# Review lenses

Use only the lenses the design touches. Each question should end in a project fact
you can cite, not an opinion.

## Contents

- Runtime and operations
- Boundaries and data ownership
- Contracts and migration
- Failure
- Fit

## Runtime and operations

- How many processes, workers, and hosts run this code? Where is that configured?
- What schedules background work today (cron, a worker, a timer)? Does the design
  use it or assume something else?
- Where does state live, and is it backed up? Does the design add state outside it?
- What happens on restart or deploy while the new code is mid-operation?

## Boundaries and data ownership

- Which module owns each table, file, or service the design touches? Is that
  written down in a decision record or module docs?
- Does the design read or write another module's data directly?
- Does a boundary in the design match a real reason to change separately, or only
  a diagram?

## Contracts and migration

- Which fields, endpoints, events, or file formats are seen outside the code that
  produces them (API routes, templates, exports, partner integrations)?
- Does the design change one of them? Is there a period when old and new both work
  (expand, migrate, contract), and who moves the callers?
- Can a partial rollout be undone without losing data?

## Failure

- Trace one failure: a dependency times out, the process dies mid-step, a job runs
  twice. What state is left, and is it what the design says?
- Are retries bounded and safe to repeat?

## Fit

- What is the simplest design that meets the stated goals in this project? If the
  proposal is more complex, what does the extra complexity buy?
- Does every new component remove a demonstrated problem?
- What would the person on call need when this breaks that the design does not give
  them?
