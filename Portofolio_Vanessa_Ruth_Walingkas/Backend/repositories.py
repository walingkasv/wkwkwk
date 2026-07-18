from __future__ import annotations

from typing import Any

from Backend.database import db


ENTITY_CONFIG = {
    "skills": {
        "table": "skills",
        "fields": ["nama_skill", "icon_class"],
        "order": "id DESC",
    },
    "experiences": {
        "table": "experiences",
        "fields": ["posisi", "perusahaan", "durasi", "deskripsi"],
        "order": "id DESC",
    },
    "projects": {
        "table": "projects",
        "fields": ["judul", "deskripsi", "gambar_url", "link_project"],
        "order": "id DESC",
    },
}


def get_user_by_username(username: str):
    return db.fetch_one("SELECT * FROM users WHERE username = ?", (username,))


def get_admin_user():
    return db.fetch_one("SELECT * FROM users WHERE role = 'admin' ORDER BY id ASC LIMIT 1")


def get_user(user_id: int):
    return db.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))


def get_profile(user_id: int):
    return db.fetch_one("SELECT * FROM profiles WHERE user_id = ?", (user_id,))


def upsert_profile(user_id: int, data: dict[str, Any]) -> None:
    existing = get_profile(user_id)
    fields = [
        "nama_lengkap", "nama_panggilan", "tempat_lahir", "tanggal_lahir", "email",
        "telepon", "universitas", "fakultas", "prodi", "semester", "alamat", "foto_url",
    ]
    values = [data.get(field) or None for field in fields]
    if existing:
        assignments = ", ".join(f"{field} = ?" for field in fields)
        db.execute(f"UPDATE profiles SET {assignments} WHERE user_id = ?", (*values, user_id))
    else:
        columns = ", ".join(["user_id", *fields])
        placeholders = ", ".join("?" for _ in range(len(fields) + 1))
        db.execute(f"INSERT INTO profiles ({columns}) VALUES ({placeholders})", (user_id, *values))


def list_entities(entity: str, user_id: int):
    config = ENTITY_CONFIG[entity]
    return db.fetch_all(
        f"SELECT * FROM {config['table']} WHERE user_id = ? ORDER BY {config['order']}",
        (user_id,),
    )


def get_entity(entity: str, item_id: int, user_id: int):
    table = ENTITY_CONFIG[entity]["table"]
    return db.fetch_one(f"SELECT * FROM {table} WHERE id = ? AND user_id = ?", (item_id, user_id))


def save_entity(entity: str, user_id: int, data: dict[str, Any], item_id: int | None = None) -> int:
    config = ENTITY_CONFIG[entity]
    fields = config["fields"]
    values = [data.get(field) or None for field in fields]
    if item_id:
        assignments = ", ".join(f"{field} = ?" for field in fields)
        db.execute(
            f"UPDATE {config['table']} SET {assignments} WHERE id = ? AND user_id = ?",
            (*values, item_id, user_id),
        )
        return item_id

    columns = ", ".join(["user_id", *fields])
    placeholders = ", ".join("?" for _ in range(len(fields) + 1))
    return db.execute(
        f"INSERT INTO {config['table']} ({columns}) VALUES ({placeholders})",
        (user_id, *values),
    )


def delete_entity(entity: str, item_id: int, user_id: int) -> None:
    table = ENTITY_CONFIG[entity]["table"]
    db.execute(f"DELETE FROM {table} WHERE id = ? AND user_id = ?", (item_id, user_id))


def public_portfolio(user_id: int) -> dict[str, Any]:
    return {
        "profile": get_profile(user_id),
        "skills": list_entities("skills", user_id),
        "experiences": list_entities("experiences", user_id),
        "projects": list_entities("projects", user_id),
    }
