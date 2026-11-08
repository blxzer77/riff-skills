export class RateLimiter {
  private hits = new Map<string, number[]>();

  constructor(private limit: number, private windowMs: number, private now = () => Date.now()) {}

  allow(key: string): boolean {
    const t = this.now();
    const recent = (this.hits.get(key) ?? []).filter((h) => t - h < this.windowMs);
    if (recent.length >= this.limit) return false;
    recent.push(t);
    this.hits.set(key, recent);
    return true;
  }
}
