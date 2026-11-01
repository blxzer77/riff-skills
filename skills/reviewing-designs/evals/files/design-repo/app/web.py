from flask import Flask, jsonify, request

from .loans import lend


def create_app(db) -> Flask:
    app = Flask(__name__)

    @app.post("/api/v1/loans")
    def post_loan():
        body = request.get_json(force=True)
        return jsonify(lend(db, body["bookId"], body["memberId"])), 201

    return app
