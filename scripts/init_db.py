"""Crea el esquema. Uso: python -m scripts.init_db"""
from app import create_app
from app.config import get_config
from app.data.db import init_schema

def main():
    app = create_app()
    with app.app_context():
        init_schema(app.config["DATABASE"], app.config["SCHEMA_PATH"])
        print(f"[OK] Esquema inicializado en {app.config['DATABASE']}")

if __name__ == "__main__":
    main()