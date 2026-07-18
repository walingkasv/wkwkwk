from __future__ import annotations

import re

from flask import Blueprint, current_app, jsonify, request

from Backend.database import db
from Backend.repositories import get_admin_user, public_portfolio
from Backend.services.email_service import configured as email_configured
from Backend.services.email_service import send_contact_email

api_bp = Blueprint("api", __name__, url_prefix="/api")
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def admin_user():
    return get_admin_user()


@api_bp.get("/health")
def health():
    return jsonify({"status": "ok", "database": current_app.config["DB_DRIVER"]})


@api_bp.get("/portfolio")
def portfolio():
    user = admin_user()
    if not user:
        return jsonify({"error": "Data admin belum tersedia."}), 404
    return jsonify(public_portfolio(user["id"]))


@api_bp.post("/contact")
def contact():
    payload = request.get_json(silent=True) or request.form.to_dict()
    if payload.get("website"):
        return jsonify({"message": "Pesan diterima."}), 200

    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    subject = str(payload.get("subject", "")).strip()
    message = str(payload.get("message", "")).strip()

    errors = []
    if not (2 <= len(name) <= 100):
        errors.append("Nama harus 2–100 karakter.")
    if not EMAIL_PATTERN.match(email) or len(email) > 100:
        errors.append("Alamat email tidak valid.")
    if len(subject) > 150:
        errors.append("Subjek maksimal 150 karakter.")
    if not (5 <= len(message) <= 4000):
        errors.append("Pesan harus 5–4000 karakter.")
    if errors:
        return jsonify({"error": " ".join(errors)}), 400

    message_id = db.execute(
        "INSERT INTO contact_messages (nama, email, subjek, pesan, status) VALUES (?, ?, ?, ?, 'baru')",
        (name, email, subject or None, message),
    )

    email_id = None
    email_error = None
    try:
        email_id = send_contact_email(name, email, subject, message)
    except Exception as exc:  # Pesan tetap tersimpan walaupun provider sedang bermasalah.
        email_error = str(exc)

    response = {
        "message": "Pesan berhasil disimpan dan dikirim." if email_id else "Pesan berhasil disimpan.",
        "id": message_id,
        "email_sent": bool(email_id),
        "email_service_configured": email_configured(),
    }
    if email_error and current_app.debug:
        response["email_error"] = email_error
    return jsonify(response), 201
