export function parseDuration(input: string): number {
  const m = input.match(/^(\d+)(h|m|s)$/);
  if (!m) return NaN;
  const n = Number(m[1]);
  return m[2] === "h" ? n * 3600 : m[2] === "m" ? n * 60 : n;
}

export function formatMoney(cents: number): string {
  return `$${(cents / 100).toFixed(2)}`;
}
