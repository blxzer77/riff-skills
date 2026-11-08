from flask import Flask, jsonify, request

from .db import Database
from .mailer import SmtpMailer
from .signup import SignupError, signup


def create_app() -> Flask:
    app = Flask(__name__)
    db = Database()
    mailer = SmtpMailer()

    @app.post("/signup")
    def post_signup():
        body = request.get_json(force=True)
        try:
            user_id = signup(db, mailer, body["email"], body["name"])
        except SignupError as exc:
            return jsonify(error=str(exc)), 400
        return jsonify(id=user_id), 201

    return app
