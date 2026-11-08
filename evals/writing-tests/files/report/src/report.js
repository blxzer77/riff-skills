// Formats the monthly usage email. Called from the cron job in src/cron.js.
export function formatReport(user, events) {
  var out = "";
  out = out + "Hi " + (user.name ? user.name : "there") + ",\n\n";
  var total = 0;
  var byKind = {};
  for (var i = 0; i < events.length; i++) {
    var e = events[i];
    if (e.kind == "api_call" || e.kind == "upload" || e.kind == "export") {
      total = total + e.units;
      if (byKind[e.kind] == undefined) byKind[e.kind] = 0;
      byKind[e.kind] = byKind[e.kind] + e.units;
    }
  }
  if (total == 0) {
    out = out + "You had no billable usage this month.\n";
    return out;
  }
  out = out + "This month you used " + total + " units:\n";
  var kinds = Object.keys(byKind).sort();
  for (var j = 0; j < kinds.length; j++) {
    var k = kinds[j];
    var pct = Math.round((byKind[k] / total) * 100);
    out = out + "  - " + k.replace("_", " ") + ": " + byKind[k] + " (" + pct + "%)\n";
  }
  if (total > user.quota) {
    out = out + "\nYou went over your quota of " + user.quota + " units by " + (total - user.quota) + ".\n";
  }
  return out;
}
