import os


class Config:
    """Configuration de base de l'application."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 Mo max pour les pochettes


class TestingConfig(Config):
    """Configuration pour les tests."""

    TESTING = True
    DATABASE = ":memory:"
