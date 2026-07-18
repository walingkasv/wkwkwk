from __future__ import annotations

import logging
import secrets

from flask import Flask, abort, request, session
from werkzeug.security import generate_password_hash

from Backend.admin.routes import admin_bp
from Backend.api.routes import api_bp
from Backend.database import db, schema_statements
from Backend.public.routes import public_bp
from config import Config

logger = logging.getLogger(__name__)


def create_app(config_object=Config):
    app = Flask(__name__, template_folder="Frontend", static_folder="Frontend")
    app.config.from_object(config_object)
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        MAX_CONTENT_LENGTH=6 * 1024 * 1024,
    )

    app.register_blueprint(public_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    @app.before_request
    def csrf_protection():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(32)
        if request.method == "POST" and request.path.startswith("/admin"):
            token = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
            if not token or not secrets.compare_digest(token, session["csrf_token"]):
                abort(400, description="Token CSRF tidak valid.")

    @app.context_processor
    def inject_globals():
        return {"csrf_token": session.get("csrf_token", "")}

    with app.app_context():
        initialize_database(app)

    return app


def initialize_database(app: Flask) -> None:
    if not app.config.get("AUTO_CREATE_TABLES", True):
        return

    try:
        if app.config["DB_DRIVER"] != "sqlite":
            required_keys = ("DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME")
            if not all(app.config.get(key) for key in required_keys):
                logger.info("Skipping database initialization because TiDB/MySQL env vars are incomplete.")
                return

        db.executescript(schema_statements(app.config["DB_DRIVER"]))
        seed_admin_and_profile(app)
    except Exception as exc:  # pragma: no cover - defensive for deployment/import safety
        logger.warning("Database initialization skipped during import/startup: %s", exc)


def seed_admin_and_profile(app: Flask) -> None:
    username = app.config["ADMIN_USERNAME"]
    user = db.fetch_one("SELECT * FROM users WHERE role = 'admin' ORDER BY id ASC LIMIT 1")
    if not user:
        user_id = db.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
            (username, generate_password_hash(app.config["ADMIN_PASSWORD"])),
        )
    else:
        user_id = user["id"]

    profile = db.fetch_one("SELECT id FROM profiles WHERE user_id = ?", (user_id,))
    if not profile:
        db.execute(
            """
            INSERT INTO profiles (
                user_id, nama_lengkap, nama_panggilan, universitas, prodi, semester, alamat
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                "Vanessa Ruth Walingkas",
                "Vanessa",
                "Isi nama universitas melalui halaman Admin",
                "Sistem Informasi",
                "Isi semester",
                "Isi alamat dan deskripsi singkat melalui halaman Admin.",
            ),
        )


app = create_app()

# WSGI entrypoint for Vercel / production hosting.
application = app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config["FLASK_DEBUG"])
