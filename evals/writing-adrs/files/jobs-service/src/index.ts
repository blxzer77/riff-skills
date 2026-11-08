import { next } from "./jobs/queue.js";
import { runJob } from "./jobs/run.js";

setInterval(async () => {
  const job = next();
  if (job) await runJob(job);
}, 250);
