from __future__ import annotations

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from Backend.auth import login_required
from Backend.database import db
from Backend.repositories import (
    delete_entity,
    get_entity,
    get_profile,
    get_user,
    get_user_by_username,
    list_entities,
    save_entity,
    upsert_profile,
)
from Backend.services.cloudinary_service import upload_image

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def current_user_id() -> int:
    return int(session["user_id"])


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("admin.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_user_by_username(username)
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Login berhasil. Selamat datang!", "success")
            return redirect(url_for("admin.dashboard"))
        flash("Username atau password salah.", "danger")
    return render_template("admin/login.html")


@admin_bp.post("/logout")
@login_required
def logout():
    session.clear()
    flash("Anda sudah logout.", "success")
    return redirect(url_for("admin.login"))


@admin_bp.get("")
@admin_bp.get("/")
@login_required
def dashboard():
    user_id = current_user_id()
    try:
        counts = {
            "skills": int((db.fetch_one("SELECT COUNT(*) AS total FROM skills WHERE user_id = ?", (user_id,)) or {}).get("total", 0)),
            "experiences": int((db.fetch_one("SELECT COUNT(*) AS total FROM experiences WHERE user_id = ?", (user_id,)) or {}).get("total", 0)),
            "projects": int((db.fetch_one("SELECT COUNT(*) AS total FROM projects WHERE user_id = ?", (user_id,)) or {}).get("total", 0)),
            "messages": int((db.fetch_one("SELECT COUNT(*) AS total FROM contact_messages WHERE status = 'baru'") or {}).get("total", 0)),
        }
        recent_messages = db.fetch_all("SELECT * FROM contact_messages ORDER BY id DESC LIMIT 5")
    except Exception:
        current_app.logger.exception("Dashboard data unavailable")
        counts = {"skills": 0, "experiences": 0, "projects": 0, "messages": 0}
        recent_messages = []
    return render_template("admin/dashboard.html", counts=counts, recent_messages=recent_messages)


@admin_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = current_user_id()
    profile_data = get_profile(user_id)
    if request.method == "POST":
        data = {key: request.form.get(key, "").strip() for key in [
            "nama_lengkap", "nama_panggilan", "tempat_lahir", "tanggal_lahir", "email",
            "telepon", "universitas", "fakultas", "prodi", "semester", "alamat", "foto_url",
        ]}
        if not data["nama_lengkap"]:
            flash("Nama lengkap wajib diisi.", "danger")
            return render_template("admin/profile.html", profile=profile_data)
        try:
            uploaded = upload_image(request.files.get("foto"), "profile")
            if uploaded:
                data["foto_url"] = uploaded
            elif not data["foto_url"] and profile_data:
                data["foto_url"] = profile_data.get("foto_url")
            upsert_profile(user_id, data)
            flash("Profil berhasil diperbarui.", "success")
            return redirect(url_for("admin.profile"))
        except (ValueError, RuntimeError) as exc:
            flash(str(exc), "danger")
        except Exception as exc:
            current_app.logger.exception("Gagal memperbarui profil")
            flash(f"Profil gagal disimpan: {exc}" if current_app.debug else "Profil gagal disimpan.", "danger")
    return render_template("admin/profile.html", profile=profile_data)


def entity_page(entity: str, template: str, fields: list[str], mandatory_fields: list[str]):
    user_id = current_user_id()
    edit_id = request.args.get("edit", type=int)
    edit_item = get_entity(entity, edit_id, user_id) if edit_id else None
    if request.method == "POST":
        item_id = request.form.get("id", type=int)
        data = {field: request.form.get(field, "").strip() for field in fields}
        if any(not data.get(field) for field in mandatory_fields):
            flash("Kolom utama wajib diisi.", "danger")
        else:
            save_entity(entity, user_id, data, item_id)
            flash("Data berhasil disimpan.", "success")
            return redirect(url_for(f"admin.{entity}"))
    return render_template(template, items=list_entities(entity, user_id), edit_item=edit_item)


@admin_bp.route("/skills", methods=["GET", "POST"])
@login_required
def skills():
    return entity_page("skills", "admin/skills.html", ["nama_skill", "icon_class"], ["nama_skill"])


@admin_bp.post("/skills/<int:item_id>/delete")
@login_required
def delete_skill(item_id: int):
    delete_entity("skills", item_id, current_user_id())
    flash("Skill berhasil dihapus.", "success")
    return redirect(url_for("admin.skills"))


@admin_bp.route("/experiences", methods=["GET", "POST"])
@login_required
def experiences():
    return entity_page("experiences", "admin/experiences.html", ["posisi", "perusahaan", "durasi", "deskripsi"], ["posisi", "perusahaan"])


@admin_bp.post("/experiences/<int:item_id>/delete")
@login_required
def delete_experience(item_id: int):
    delete_entity("experiences", item_id, current_user_id())
    flash("Pengalaman berhasil dihapus.", "success")
    return redirect(url_for("admin.experiences"))


@admin_bp.route("/projects", methods=["GET", "POST"])
@login_required
def projects():
    user_id = current_user_id()
    edit_id = request.args.get("edit", type=int)
    edit_item = get_entity("projects", edit_id, user_id) if edit_id else None
    if request.method == "POST":
        item_id = request.form.get("id", type=int)
        existing = get_entity("projects", item_id, user_id) if item_id else None
        data = {
            "judul": request.form.get("judul", "").strip(),
            "deskripsi": request.form.get("deskripsi", "").strip(),
            "gambar_url": request.form.get("gambar_url", "").strip(),
            "link_project": request.form.get("link_project", "").strip(),
        }
        if not data["judul"]:
            flash("Judul proyek wajib diisi.", "danger")
        else:
            try:
                uploaded = upload_image(request.files.get("gambar"), "projects")
                if uploaded:
                    data["gambar_url"] = uploaded
                elif not data["gambar_url"] and existing:
                    data["gambar_url"] = existing.get("gambar_url")
                save_entity("projects", user_id, data, item_id)
                flash("Proyek berhasil disimpan.", "success")
                return redirect(url_for("admin.projects"))
            except (ValueError, RuntimeError) as exc:
                flash(str(exc), "danger")
            except Exception as exc:
                current_app.logger.exception("Gagal menyimpan proyek")
                flash(f"Proyek gagal disimpan: {exc}" if current_app.debug else "Proyek gagal disimpan.", "danger")
    return render_template("admin/projects.html", items=list_entities("projects", user_id), edit_item=edit_item)


@admin_bp.post("/projects/<int:item_id>/delete")
@login_required
def delete_project(item_id: int):
    delete_entity("projects", item_id, current_user_id())
    flash("Proyek berhasil dihapus.", "success")
    return redirect(url_for("admin.projects"))


@admin_bp.route("/messages", methods=["GET"])
@login_required
def messages():
    try:
        items = db.fetch_all("SELECT * FROM contact_messages ORDER BY id DESC")
    except Exception:
        current_app.logger.exception("Unable to load messages")
        items = []
    return render_template("admin/messages.html", items=items)


@admin_bp.post("/messages/<int:item_id>/toggle")
@login_required
def toggle_message(item_id: int):
    try:
        item = db.fetch_one("SELECT status FROM contact_messages WHERE id = ?", (item_id,))
        if item:
            new_status = "dibaca" if item["status"] == "baru" else "baru"
            db.execute("UPDATE contact_messages SET status = ? WHERE id = ?", (new_status, item_id))
        flash("Status pesan diperbarui.", "success")
    except Exception:
        current_app.logger.exception("Unable to toggle message")
        flash("Gagal memperbarui status pesan.", "danger")
    return redirect(url_for("admin.messages"))


@admin_bp.post("/messages/<int:item_id>/delete")
@login_required
def delete_message(item_id: int):
    try:
        db.execute("DELETE FROM contact_messages WHERE id = ?", (item_id,))
        flash("Pesan berhasil dihapus.", "success")
    except Exception:
        current_app.logger.exception("Unable to delete message")
        flash("Gagal menghapus pesan.", "danger")
    return redirect(url_for("admin.messages"))


@admin_bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    user = get_user(current_user_id())
    if not user:
        flash("Tidak dapat memuat akun saat ini.", "danger")
        return render_template("admin/account.html", user=None)
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        old_password = request.form.get("old_password", "")
        new_password = request.form.get("new_password", "")
        if not username:
            flash("Username wajib diisi.", "danger")
        elif get_user_by_username(username) and username != user["username"]:
            flash("Username sudah digunakan.", "danger")
        elif new_password and not check_password_hash(user["password_hash"], old_password):
            flash("Password lama tidak sesuai.", "danger")
        elif new_password and len(new_password) < 6:
            flash("Password baru minimal 6 karakter.", "danger")
        else:
            if new_password:
                db.execute(
                    "UPDATE users SET username = ?, password_hash = ? WHERE id = ?",
                    (username, generate_password_hash(new_password), user["id"]),
                )
            else:
                db.execute("UPDATE users SET username = ? WHERE id = ?", (username, user["id"]))
            session["username"] = username
            flash("Akun berhasil diperbarui.", "success")
            return redirect(url_for("admin.account"))
    return render_template("admin/account.html", user=user)
