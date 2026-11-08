## Design review

Before building a non-trivial design, check its load-bearing claims against the
repository: how the app actually runs (processes, schedulers, hosts), who owns the
data it touches, which fields and endpoints callers outside the change depend on,
and the accepted decision records. Report only findings you can tie to both the
design's text and a project file; skip taste, preferred patterns, and speculative
scale. End with one verdict: approve, approve with changes, or do not approve.
