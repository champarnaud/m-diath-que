import os


class Config:
    """Configuration de base de l'application."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    DATABASE = os.environ.get("DATABASE", "instance/mediatheque.db")
    UPLOAD_FOLDER = os.path.join("app", "static", "uploads")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 Mo max pour les pochettes


class TestingConfig(Config):
    """Configuration pour les tests."""

    TESTING = True
    DATABASE = ":memory:"
