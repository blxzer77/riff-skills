# How I cut a release (notes for myself)

- check main is green
- bump version in Cargo.toml AND in npm/package.json (the npm wrapper), they drift apart every time I forget the second one
- `cargo build --release` then `./scripts/pack.sh` makes the tarballs in dist/
- tag must be vX.Y.Z, the CI release workflow only triggers on that pattern (I once pushed X.Y.Z without v and nothing happened)
- changelog: take merged PR titles since last tag, group feat/fix/other, drop chore: ones
- after the GH release is up, `npm publish` from npm/ — needs the tarball URLs to exist first or the postinstall 404s
- announce in #releases
