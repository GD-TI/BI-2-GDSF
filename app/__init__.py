from __future__ import annotations

from flask import Flask
from flask_cors import CORS

from app.api.routes import bp


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        allow_headers=["Content-Type", "apikey"],
        methods=["GET", "POST", "OPTIONS"],
    )
    app.register_blueprint(bp)
    return app
