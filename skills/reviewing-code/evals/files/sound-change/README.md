# billing

Invoice arithmetic for an internal billing job. Callers pass a discount chosen by
finance staff in the admin console. Amounts are `Decimal`; rounding to cents uses
half-up, matching the accounting policy.

`review.patch` is the pending change; `src/` and `tests/` have it applied. Run tests
with `python3 -m unittest`.

PR description: "Support an optional whole-invoice percentage discount."
