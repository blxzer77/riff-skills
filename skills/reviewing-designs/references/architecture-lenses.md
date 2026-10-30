# Architecture review lenses

Use only lenses affected by the proposal.

## Boundaries

- Who owns each module and its data?
- Does a change require touching unrelated modules?
- Are dependencies pointing toward stable policy or volatile details?
- Is the boundary justified by change, ownership, scaling, or deployment needs?

## Evolution

- Can the public contract be extended without breaking existing clients?
- Is there an expand/migrate/contract path for data and APIs?
- Can the change be rolled back after partial deployment?
- What assumption triggers a revisit?

## Failure

- What if the dependency times out, returns a duplicate, or is unavailable?
- What state is durable after a crash?
- Are retries safe and bounded? Are partial results visible?
- What test or rehearsal demonstrates recovery?

## Complexity

- What new concepts, processes, services, and failure modes are introduced?
- Does each layer or service remove a demonstrated risk?
- Could a simpler design meet the same must-haves now?

Never treat these as a compliance checklist. A lens that is irrelevant to the design
should be marked not applicable with a reason.
