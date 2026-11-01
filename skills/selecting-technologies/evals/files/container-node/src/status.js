const components = [
  { name: "booking-api", state: "operational" },
  { name: "payments", state: "operational" },
  { name: "notifications", state: "degraded" },
];

function status() {
  const worst = components.some((c) => c.state !== "operational") ? "degraded" : "operational";
  return { overall: worst, components };
}

module.exports = { status };
