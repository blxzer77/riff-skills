from functools import wraps

from flask import abort, session


def login_required(view):
    """Allow the request when the session carries a volunteer id."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        if "volunteer_id" not in session:
            abort(401)
        return view(*args, **kwargs)

    return wrapper
