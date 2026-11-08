from flask import Blueprint, request, session

from .db import connect
from .passwords import verify

bp = Blueprint("auth", __name__)


@bp.post("/login")
def login():
    email = request.form["email"]
    row = connect().execute(
        "SELECT id, password_hash FROM volunteers WHERE email = ?", (email,)
    ).fetchone()
    if row is None or not verify(request.form["password"], row["password_hash"]):
        return {"error": "invalid credentials"}, 401
    session["volunteer_id"] = row["id"]
    return {"ok": True}
