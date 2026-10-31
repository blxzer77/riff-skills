# Migration review fixture

`review.patch` is the proposed migration and the files under `migrations/` and
`tests/` are the supplied post-change artifacts. The orders table is large, the
release job runs migration statements without an explicit transaction, and an old
application version remains live during a rolling deploy. The tests cover only
successful up-migration data mapping; rollback, interruption, and old-client
behavior are intentionally part of the review scope.
