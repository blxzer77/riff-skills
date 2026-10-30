# Flaky tests

A flaky test passes and fails on the same code. It trains everyone to ignore red
builds, so it is a defect to fix, not a nuisance to retry.

Source: Martin Fowler, "Eradicating Non-Determinism in Tests"
(https://martinfowler.com/articles/nonDeterminism.html); Software Engineering at
Google, ch. 11 (https://abseil.io/resources/swe-book/html/ch11.html).

## Diagnose

1. Reproduce: run the single test in a loop (20–50 times), then the whole file, then
   in random order or in parallel if the runner supports it. Note which mode fails.
2. Fails alone → the cause is inside the test or the code (time, randomness, async).
   Fails only with others → shared state or ordering.
3. Read the failure values; they usually name the race (an off-by-one millisecond,
   a missing row, a stale cache).

## Causes and fixes

| Cause | Symptom | Fix |
|---|---|---|
| Real time | expiry, timeouts, "today" logic fails near boundaries | inject a clock or use the runner's fake timers; advance time explicitly; test both sides of the boundary |
| Sleeping for async work | passes on fast machines | wait on the actual signal: await the promise, poll a condition with a timeout, use a callback |
| Unseeded randomness | rare failures with odd values | seed it, or inject the random source; for property tests, keep the failing seed |
| Shared state | fails depending on order | build fresh state per test (new DB schema/transaction, temp dirs); do not rely on cleanup |
| Remote services | network errors, rate limits | fake at the boundary; verify the fake with a contract test |
| Concurrency in the code | intermittent wrong results | the bug is real; reproduce with controlled scheduling or many iterations, then fix the code |
| Leaked resources | later tests time out | close handles in the code under test; pool or scope resources |

## Rules

- Never fix flakiness by adding retries, raising sleeps, or loosening assertions;
  those hide the race and the next one.
- Keep the behavior covered. A fix that deletes the expiry check makes the test
  stable and useless; confirm the test still fails when the behavior is broken.
- If a fix will take time, quarantine the test (skip with a tracked reason) rather
  than leaving it in the main suite, and keep the quarantine small and short-lived.
