import type { Job } from "./queue.js";

export async function runJob(job: Job): Promise<void> {
  // thumbnail and email handlers elided
  console.log("running", job.kind, job.id);
}
