# Incremental migration

Verified on 2026-11-01. Adapted from the sources in `sources.md`.

Keep the system building and passing its tests at every step. A migration that
needs a long-lived branch or a big-bang switch is a rewrite in disguise.

## Branch by abstraction (replace an implementation)

1. Put an interface in front of the current implementation where callers use it.
2. Move every caller to the interface, one at a time.
3. Write the new implementation behind the same interface; switch callers to it
   gradually, or behind a toggle.
4. Delete the old implementation once nothing uses it, and remove the interface if
   it no longer earns its keep.

## Strangler fig (extract or replace a capability)

1. Route calls for the capability through one seam you control.
2. Build the new module behind that seam with its own public interface and data.
3. Shift traffic or callers over in small, reversible slices, comparing results.
4. Retire the old path and delete its code; a migration is finished only when the
   old code is gone.

## Every plan names

The public interface callers will use, who owns the data during and after the move,
how each step is rolled back, how you will know the old path is unused, and when it
will be deleted.
