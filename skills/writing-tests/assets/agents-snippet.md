## Tests

A change that alters behavior is not done until a test would fail without it.

- Bug fix: first write a test that reproduces the bug and watch it fail, then fix.
- New behavior: add tests through the public interface for the normal case, the
  boundaries, and the error paths that matter.
- Refactor: existing tests must pass unchanged; add characterization tests first if
  the code is untested.
- Never weaken, skip, or delete a failing test to get green; fix the cause or ask.
- Run the relevant tests before reporting done, and say which ones ran.
