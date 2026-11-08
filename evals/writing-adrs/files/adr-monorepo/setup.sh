#!/usr/bin/env bash
# Tags the fixture as v2.3.0 and adds merged-PR commits after it, so "the changelog
# entry for v2.4.0 from the merged PRs since the last tag" has history to read.
# Removed from the sandbox before the agent runs.
set -euo pipefail
git tag v2.3.0
echo "// shelves" >> packages/web/src/store/lists.ts
git commit -qam "Merge pull request #212 from mia/shelves: add shelves to reading lists"
echo "// rate limit" >> services/gateway/src/middleware/errors.ts
git commit -qam "Merge pull request #215 from ken/rate-limit: return 429 on burst traffic"
echo "// dark mode" >> packages/desktop/src/db.ts
git commit -qam "Merge pull request #218 from ana/desktop-dark: dark mode in the desktop app"
