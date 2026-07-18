import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-this")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"

    # Database: gunakan "tidb" untuk pengumpulan, "sqlite" untuk demo lokal cepat.
    DB_DRIVER = os.getenv("DB_DRIVER", "sqlite").lower()
    DB_HOST = os.getenv("DB_HOST", "")
    DB_PORT = int(os.getenv("DB_PORT", "4000"))
    DB_USER = os.getenv("DB_USER", "")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "portfolio_vanessa")
    DB_CA_PATH = os.getenv("DB_CA_PATH", "")
    SQLITE_PATH = os.getenv("SQLITE_PATH", str(BASE_DIR / "portfolio_local.db"))
    AUTO_CREATE_TABLES = os.getenv("AUTO_CREATE_TABLES", "true").lower() == "true"

    # Cloudinary
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")
    CLOUDINARY_FOLDER = os.getenv("CLOUDINARY_FOLDER", "portfolio_vanessa")

    # Resend
    RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
    RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "Portfolio Vanessa <onboarding@resend.dev>")
    RESEND_TO_EMAIL = os.getenv("RESEND_TO_EMAIL", "")

    # Akun awal admin. Ganti sesudah login pertama.
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
