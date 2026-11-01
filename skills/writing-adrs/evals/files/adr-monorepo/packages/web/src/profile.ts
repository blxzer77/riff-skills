export async function getUserData(id: number) {
  const res = await fetch(`/api/users/${id}`);
  return res.json();
}
