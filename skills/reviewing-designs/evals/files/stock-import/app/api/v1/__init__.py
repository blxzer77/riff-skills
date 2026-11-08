from flask import Blueprint

bp = Blueprint("api_v1", __name__)

from . import households  # noqa: E402,F401  (registers routes)
