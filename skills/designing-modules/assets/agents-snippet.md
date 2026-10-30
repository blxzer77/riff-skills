# Always-on module behavior

- Before splitting code, inspect the repository and name the concrete change or operational pressure the split addresses.
- Prefer the smallest scale that satisfies current constraints: clear seams first, modular monolith before services.
- Keep capabilities as vertical slices with owned data, narrow contracts, explicit dependency direction, and boundary checks.
- For migrations, define rollout, rollback, ownership, and deletion criteria; stop when a boundary has no independent reason to exist.
