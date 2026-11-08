export type Job = { id: string; kind: "thumbnail" | "email"; payload: unknown; attempts: number };

// In-memory FIFO. Jobs are lost when the process restarts.
const pending: Job[] = [];

export function enqueue(job: Omit<Job, "attempts">): void {
  pending.push({ ...job, attempts: 0 });
}

export function next(): Job | undefined {
  return pending.shift();
}

export function size(): number {
  return pending.length;
}
