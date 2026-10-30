# Technology scorecard

Use this as a structured conversation, not a calculator. A candidate that fails a
must-have is out. Weight only criteria that matter to this project.

| Criterion | Question | Evidence |
|---|---|---|
| Requirement fit | Does it satisfy the must-have workload and quality goals? | Project spike, official limits, production evidence |
| Complexity | What concepts, code, and operations does it add? | Minimal prototype and existing team experience |
| Maturity | Is the release line stable and the upgrade path clear? | Official support policy, release history |
| Maintenance | Will fixes, docs, and compatibility continue? | Maintainer activity, issue response, bus factor |
| Ecosystem | Can the project hire, debug, and integrate around it? | Docs, examples, compatible libraries, team familiarity |
| Security | How are advisories, defaults, updates, and secrets handled? | Official advisories and security docs |
| Operability | Can this project run, observe, back up, and recover it? | Local deployment and failure drill |
| Portability | How hard is it to move away? | Data export, standard protocols, adapter boundary |
| Cost | What is paid now and what scales with usage? | Current pricing checked from official source |
| Reversibility | What must be rewritten if this is wrong? | Dependency graph and migration sketch |

For each High/Medium/Low judgment, write one sentence of evidence or mark it
unknown. Separate **fit** (how well it solves today's problem) from **confidence**
(how strong the evidence is).

## Stop conditions

Do not choose yet when:

- no candidate meets a must-have;
- the main comparison depends on an unmeasured workload;
- the only argument for a candidate is novelty, popularity, or a benchmark unrelated
  to the project;
- the exit path for a sticky dependency is unknown and the decision is reversible
  only at high cost.

Time-box a spike and define what result changes the choice.
