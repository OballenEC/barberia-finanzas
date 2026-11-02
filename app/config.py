import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-key-change-me")
    DATABASE = str(BASE_DIR / os.getenv("DATABASE_PATH", "instance/barberia.sqlite3"))
    DEMO_MODE = os.getenv("DEMO_MODE", "1") == "1"
    WEEK_START = os.getenv("WEEK_START", "mon")  # mon|sun
    SCHEMA_PATH = str(BASE_DIR / "app" / "data" / "schema.sql")

class DevelopmentConfig(BaseConfig):
    DEBUG = True

class TestingConfig(BaseConfig):
    TESTING = True
    DATABASE = ":memory:"
    DEMO_MODE = False

class ProductionConfig(BaseConfig):
    DEBUG = False

_CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

def get_config(name: str | None = None):
    return _CONFIGS.get(name or "development", DevelopmentConfig)