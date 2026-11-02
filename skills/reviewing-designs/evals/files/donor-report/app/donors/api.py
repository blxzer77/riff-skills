"""Public functions of the donors module. Other modules call these."""

from ..db import connect


def donations_between(start: str, end: str) -> list[dict]:
    rows = connect().execute(
        "SELECT d.id, d.donor_id, n.name AS donor_name, d.received_at "
        "FROM donations d JOIN donors n ON n.id = d.donor_id "
        "WHERE d.received_at >= ? AND d.received_at < ?",
        (start, end),
    ).fetchall()
    return [dict(r) for r in rows]
