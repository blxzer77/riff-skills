const test = require("node:test");
const assert = require("node:assert");
const { status } = require("../src/status");

test("overall is degraded when any component is degraded", () => {
  assert.strictEqual(status().overall, "degraded");
});
