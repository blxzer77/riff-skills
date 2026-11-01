---
name: selecting-technologies
description: Chooses which library, runtime version, base image, datastore, queue, hosting service, or model to use, and checks that choice against the project and against current release, end-of-life, and deprecation facts rather than memory. Use when adding a dependency, picking a version or image tag, wiring in an external service or LLM model, replacing a framework or datastore, or when the user asks which option to use, even if they only ask to "add", "switch to", or "set up" something. Not for code changes that use only what the project already depends on.
license: Apache-2.0
metadata:
  verified-on: "2026-11-02"
---

# Selecting technologies

A technology choice made from memory is made with stale facts. Versions reach end
of life, packages stop being released, models are retired, and the obvious answer
from a year ago can now fail at install time. Before naming a dependency, version,
or model, check what the project already has and what is true today.

## Workflow

1. **Read the project first.** Manifests and lockfiles, deployment files (compose,
   Dockerfile, CI, infrastructure), README and contributing notes, existing ADRs,
   and neighbouring code. Record the stack, how it is deployed and backed up, and
   who operates it. Constraints often live only here: how many hosts, who is on
   call, what gets backed up, which runtime version is pinned.
2. **Prefer what is already there.** If the existing stack covers the need, use it
   and stop: no comparison, no new dependency, no ADR. Otherwise prefer the
   option that adds the fewest new things to run, back up, upgrade, and learn.
   A new stateful service (broker, cache, search engine) is a large cost for a
   small team; say what it buys before adding one.
3. **Check every fact that ages, at run time.** For each candidate dependency,
   version, image, or model, look up the current state before writing it into
   code. See `references/checking-facts.md` for where and how. At minimum:
   - **Maintained**: a release in roughly the last year; not archived or marked
     deprecated; the registry name is the real project, not a look-alike.
   - **Supported version**: the runtime or base-image line has not reached end of
     life; production uses an LTS line where the project offers one.
   - **Model IDs**: the ID appears as active on the provider's current model or
     deprecation page. Do not use an ID you cannot find there.
   - **Advisories**: no known unfixed vulnerability in the version you add.
   - **Works here**: it installs and runs on the project's runtime version.
   If you cannot reach the network, say which facts are unchecked and mark them
   in the code or the reply; do not present remembered versions as current.
4. **Decide in proportion.** A small, reversible choice (one library behind a
   function, a patch-level version) needs one sentence of reasoning. A sticky
   choice (datastore, language, framework, hosted service, public protocol)
   needs 2–4 real candidates, the deciding constraint, the exit path, and an ADR
   (use `writing-adrs` if available). If the user said "whatever is best" for a
   sticky choice, recommend one and confirm before building on it.
5. **Verify the choice works.** Install it fresh from the manifest you edited and
   run the tests. Tests must not call live services; use a fake client.
6. **Report briefly.** Name what you chose, the facts you checked and when, and
   anything left unverified.

## Defaults

| Situation | Default |
|---|---|
| The project already has a library for this job | Use it |
| Background work, existing database, no ops staff | A queue or job table on the existing database, or in-process, before a new broker |
| New runtime, base image, or version pin | The newest LTS line that is supported today and that the project's code runs on |
| New package | A maintained, stable release; the standard library when it does the job well |
| LLM model ID | An active model from the provider's current list, matching the task's needs |
| Emerging technology | A time-boxed spike behind a small interface, not a migration |

## Gotchas

- A version floor in the manifest (`engines`, `python_requires`) is the oldest
  version the code tolerates, not the version to deploy.
- A package that tutorials still recommend may have had no release for years and
  may break with current versions of its own dependencies. Release date and a
  clean install settle it; reputation does not.
- Model IDs, prices, and limits are among the fastest-ageing facts. Look them up
  every time.
- Popularity, a benchmark on someone else's workload, or "everyone is moving to
  it" is not evidence of fit here.
- Adding a service to solve a problem the existing database solves trades a small
  code change for a permanent operational cost.

## References

- `references/checking-facts.md` — where to check maintenance, end of life, model
  status, advisories, and package names, with commands per ecosystem.
- `references/sticky-decisions.md` — comparing candidates, exit paths, and spikes
  for choices that are costly to reverse.
- `references/sources.md` — the published guidance this skill follows.
- `assets/agents-snippet.md` — always-on project rule for technology choices.
