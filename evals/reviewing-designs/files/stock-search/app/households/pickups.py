from datetime import datetime, timezone

from ..db import connect


def book(household_id: int, slot_start: datetime) -> int:
    """Book a pickup. Slots are stored as ISO 8601 UTC strings, e.g. 2026-11-03T15:00:00+00:00."""
    value = slot_start.astimezone(timezone.utc).isoformat(timespec="seconds")
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO pickups (household_id, slot_start) VALUES (?, ?)", (household_id, value)
        )
        return cur.lastrowid


def pickups_between(start: str, end: str) -> list[dict]:
    rows = connect().execute(
        "SELECT p.id, p.slot_start, p.reminded_at, h.name, h.email "
        "FROM pickups p JOIN households h ON h.id = p.household_id "
        "WHERE p.slot_start >= ? AND p.slot_start < ?",
        (start, end),
    ).fetchall()
    return [dict(r) for r in rows]
