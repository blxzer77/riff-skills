# Checking facts that age

Look these up at the time of the decision and note the date. Commands and endpoints
below were verified on 2026-11-02; if one fails, find the registry's current
documentation instead of falling back to memory.

## Contents

- Maintenance and release recency
- Package identity
- Runtime and image end of life
- Model IDs
- Vulnerabilities
- Works on this project

## Maintenance and release recency

OpenSSF's evaluation guide asks for a release and significant activity within the
previous 12 months, and treats 0.x, alpha, or beta versions as a stability signal.
These are prompts to investigate, not automatic rejections: a small, finished
utility can be healthy without releases. A large or security-relevant package with
no release for years is a problem, especially when its dependencies keep moving.

| Ecosystem | Release dates | Deprecation flag |
|---|---|---|
| PyPI | `GET https://pypi.org/pypi/<name>/json` (per-file `upload_time`, `yanked`); `pip index versions <name>` | Project page, classifiers ("Inactive"), repository archive status |
| npm | `npm view <name> time` | `npm view <name> deprecated` |
| crates.io | `GET https://crates.io/api/v1/crates/<name>` | yanked versions in the same response |
| Go | `GET https://proxy.golang.org/<module>/@v/list`, then `.../@v/<version>.info` | `// Deprecated:` in go.mod |
| RubyGems | `GET https://rubygems.org/api/v1/versions/<name>.json` | yanked versions |

Also check whether the source repository is archived (for GitHub:
`gh repo view <owner>/<repo> --json isArchived,pushedAt`).

## Package identity

Typosquatting targets exactly this step. Confirm the name you install is the
project's documented package name, that a similarly named package is not the more
popular one, and that the repository linked from the registry is the real upstream
rather than a personal fork.

## Runtime and image end of life

- Node.js publishes its schedule at
  `https://raw.githubusercontent.com/nodejs/Release/main/schedule.json` and states
  that production applications should use only Active LTS or Maintenance LTS
  releases. Odd-numbered and Current releases are not for production.
- Python versions: `https://devguide.python.org/versions/`.
- Many products: `GET https://endoflife.date/api/v1/products/<product>` (fields
  `isEol`, `eolFrom`, `isLts`). Gate on `isEol`/`eolFrom`; `isMaintained` also
  counts paid extended support.

For a base image, the image tag's major version decides support. Check that the
code runs on the version you choose; the manifest's minimum version is not a
recommendation.

## Model IDs

Use the provider's own pages, checked now:

- Anthropic: models overview (`https://platform.claude.com/docs/en/models/overview`),
  model deprecations (`https://platform.claude.com/docs/en/about-claude/model-deprecations`),
  or the Models API (`GET /v1/models`) with a key. A model listed as deprecated
  already has a retirement date; do not start new code on it. On Bedrock or
  Vertex AI, use that platform's IDs and lifecycle, which differ.
- Other providers publish equivalent model and deprecation pages; use theirs.

If the page cannot be reached, leave the model ID in one configurable place and
say it is unverified.

## Vulnerabilities

- Any ecosystem: `POST https://api.osv.dev/v1/query` with
  `{"package": {"name": "<name>", "ecosystem": "PyPI"}, "version": "<v>"}`.
- deps.dev shows advisories and OpenSSF Scorecard results per package.
- Ecosystem tools where installed: `pip-audit`, `npm audit`, `cargo audit`,
  `govulncheck`.

## Works on this project

Install from the manifest you edited into a clean environment, on the project's
runtime version, and run the tests. A dependency whose import or first call fails
against the current versions of its own dependencies is not an option, however
often it is recommended.
