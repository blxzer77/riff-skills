# Choosing the scale

Verified on 2026-11-01. Adapted from the sources in `sources.md`.

## Monolith first

Start a new system as one deployable, built with modules that have clear public
interfaces and owned data. Boundaries are hard to get right before the domain is
understood, and moving functionality between services is far harder than moving it
between modules in one process. Fowler calls the evidence for this tentative but
consistent; treat it as a strong default, not a law.

## When a service is justified

Extract a capability only for a need that one process cannot meet:

- it must scale, deploy, or fail independently of the rest;
- a different team must own and release it on its own schedule;
- a compliance or isolation requirement forces a separate runtime.

A large codebase is not by itself a reason. Remote calls are slower and fail in ways
in-process calls do not, so service interfaces must be coarser, and every boundary
adds deployment, monitoring, and data-consistency work.

## Before extracting

The module must already behave like a service inside the monolith: callers use only
its public interface, it owns its data, and no other module reads its tables. If that
is not true yet, fix it in the monolith first; extraction will not fix it.
