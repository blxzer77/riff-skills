export function requireRole(user: { roles: string[] } | null, role: string): boolean {
  if (!user) return false;
  return user.roles.includes(role);
}
