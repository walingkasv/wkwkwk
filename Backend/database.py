from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable

import certifi
import pymysql
from flask import current_app


class Database:
    """Database helper yang mendukung SQLite untuk demo dan TiDB/MySQL untuk produksi."""

    @property
    def driver(self) -> str:
        return current_app.config["DB_DRIVER"]

    def _connect(self):
        if self.driver == "sqlite":
            path = Path(current_app.config["SQLITE_PATH"])
            path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            return conn

        configured_ca = current_app.config.get("DB_CA_PATH")
        ca_path = configured_ca if configured_ca and Path(configured_ca).is_file() else certifi.where()
        return pymysql.connect(
            host=current_app.config["DB_HOST"],
            port=current_app.config["DB_PORT"],
            user=current_app.config["DB_USER"],
            password=current_app.config["DB_PASSWORD"],
            database=current_app.config["DB_NAME"],
            cursorclass=pymysql.cursors.DictCursor,
            charset="utf8mb4",
            autocommit=False,
            ssl={"ca": ca_path},
            connect_timeout=15,
            read_timeout=20,
            write_timeout=20,
        )

    def _sql(self, query: str) -> str:
        return query if self.driver == "sqlite" else query.replace("?", "%s")

    @contextmanager
    def connection(self):
        conn = self._connect()
        try:
            yield conn
        finally:
            conn.close()

    def fetch_all(self, query: str, params: Iterable[Any] = ()) -> list[dict[str, Any]]:
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(self._sql(query), tuple(params))
            rows = cursor.fetchall()
            cursor.close()
            return [dict(row) for row in rows]

    def fetch_one(self, query: str, params: Iterable[Any] = ()) -> dict[str, Any] | None:
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(self._sql(query), tuple(params))
            row = cursor.fetchone()
            cursor.close()
            return dict(row) if row else None

    def execute(self, query: str, params: Iterable[Any] = ()) -> int:
        with self.connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(self._sql(query), tuple(params))
                last_id = int(cursor.lastrowid or 0)
                conn.commit()
                return last_id
            except Exception:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def executescript(self, statements: list[str]) -> None:
        with self.connection() as conn:
            cursor = conn.cursor()
            try:
                for statement in statements:
                    cursor.execute(self._sql(statement))
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                cursor.close()


db = Database()


def schema_statements(driver: str) -> list[str]:
    if driver == "sqlite":
        pk = "INTEGER PRIMARY KEY AUTOINCREMENT"
        timestamp = "DATETIME DEFAULT CURRENT_TIMESTAMP"
    else:
        pk = "BIGINT PRIMARY KEY AUTO_INCREMENT"
        timestamp = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"

    return [
        f"""
        CREATE TABLE IF NOT EXISTS users (
            id {pk},
            username VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(10) NOT NULL DEFAULT 'admin',
            created_at {timestamp}
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS profiles (
            id {pk},
            user_id BIGINT NOT NULL UNIQUE,
            nama_lengkap VARCHAR(100) NOT NULL,
            nama_panggilan VARCHAR(50),
            tempat_lahir VARCHAR(50),
            tanggal_lahir DATE,
            email VARCHAR(100),
            telepon VARCHAR(20),
            universitas VARCHAR(100),
            fakultas VARCHAR(100),
            prodi VARCHAR(100),
            semester VARCHAR(20),
            alamat VARCHAR(4000),
            foto_url VARCHAR(255),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS skills (
            id {pk},
            user_id BIGINT NOT NULL,
            nama_skill VARCHAR(50) NOT NULL,
            icon_class VARCHAR(50),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS experiences (
            id {pk},
            user_id BIGINT NOT NULL,
            posisi VARCHAR(100) NOT NULL,
            perusahaan VARCHAR(100) NOT NULL,
            durasi VARCHAR(50),
            deskripsi VARCHAR(4000),
            created_at {timestamp},
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS projects (
            id {pk},
            user_id BIGINT NOT NULL,
            judul VARCHAR(100) NOT NULL,
            deskripsi VARCHAR(4000),
            gambar_url VARCHAR(255),
            link_project VARCHAR(255),
            created_at {timestamp},
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS contact_messages (
            id {pk},
            nama VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            subjek VARCHAR(150),
            pesan VARCHAR(4000) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'baru',
            created_at {timestamp}
        )
        """,
    ]
