from ..db import connect
from .models import Household


def load(household_id: int) -> Household | None:
    row = connect().execute(
        "SELECT id, customer_ref, name, email, size FROM households WHERE id = ?",
        (household_id,),
    ).fetchone()
    return Household(**dict(row)) if row else None
