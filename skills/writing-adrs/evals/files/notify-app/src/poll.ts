export async function poll(since: number) {
  const res = await fetch(`/api/notifications?since=${since}`);
  return res.json();
}
