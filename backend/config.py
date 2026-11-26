import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")

    DB_SERVER = os.getenv("DB_SERVER", "127.0.0.1,1433")
    DB_NAME = os.getenv("DB_NAME", "campus_trade")
    DB_USER = os.getenv("DB_USER", "sa")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_SERVER}/{DB_NAME}"
        f"?driver={quote_plus(DB_DRIVER)}&TrustServerCertificate=yes&Encrypt=yes"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 1800}

    CORS_ORIGINS = ["http://localhost:2064", "http://127.0.0.1:2064"]

    JWT_DAYS = 1            # 普通登录有效期
    JWT_REMEMBER_DAYS = 30  # 勾选「记住我」的有效期

    UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 请求体上限 10MB（发布可带 4 张图）
