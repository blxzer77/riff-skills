#!/usr/bin/env bash
# Leaves a feature branch with a commit so "this PR diff" has a change to review.
# Removed from the sandbox before the agent runs.
set -euo pipefail
git checkout -q -b feature/order-export
cat >> server/routes/orders.js <<'JS'

router.get("/export", async (req, res) => {
  const rows = await db.allOrders();
  res.type("text/csv").send(rows.map((o) => `${o.id},${o.total}`).join("\n") + req.query.footer);
});
JS
git commit -qam "Add CSV order export"
