import os

from flask import Flask

from .api.v1 import bp as api_v1
from .auth import bp as auth
from .cli import register
from .inventory.views import bp as inventory


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ["PANTRY_SECRET_KEY"]
    app.register_blueprint(auth)
    app.register_blueprint(inventory)
    app.register_blueprint(api_v1, url_prefix="/api/v1")
    register(app)
    return app
