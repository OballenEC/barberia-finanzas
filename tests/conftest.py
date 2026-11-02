"""Fixtures compartidos para pytest.

Cada test corre con su propia BD SQLite en archivo temporal para evitar
interferencia. Los tests NO usan create_app() a menos que se requiera
(para el test de persistencia). En su lugar, usan las funciones de
dominio directamente con una conexión limpia.
"""
import sqlite3
import tempfile
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = BASE_DIR / "app" / "data" / "schema.sql"


def _cargar_schema(conn):
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()


def _cargar_catalogos(conn):
    sql = (BASE_DIR / "app" / "data" / "seed_demo.sql").read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()


@pytest.fixture
def conn():
    """Conexión SQLite en archivo temporal con schema cargado y catálogos demo.

    Se elimina al final del test. Aislada entre tests.
    """
    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
    tmp.close()
    db_path = tmp.name

    c = sqlite3.connect(db_path)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    _cargar_schema(c)
    _cargar_catalogos(c)

    try:
        yield c
    finally:
        c.close()
        Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def conn_vacia():
    """Conexión SQLite en archivo temporal SOLO con schema (sin catálogos)."""
    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
    tmp.close()
    db_path = tmp.name

    c = sqlite3.connect(db_path)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    _cargar_schema(c)

    try:
        yield c
    finally:
        c.close()
        Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def helpers(conn):
    """Helpers para que los tests no repitan código de setup."""
    conn.row_factory = sqlite3.Row

    def get_id_servicio(nombre):
        return conn.execute(
            "SELECT id FROM servicios WHERE nombre = ?", (nombre,)
        ).fetchone()["id"]

    def get_id_producto(codigo):
        return conn.execute(
            "SELECT id FROM productos WHERE codigo_interno = ?", (codigo,)
        ).fetchone()["id"]

    def crear_barbero(nombre, pct):
        from app.domain import barberos as dom_barberos
        return dom_barberos.crear_barbero(
            conn, nombre=nombre, comision_pct_default=pct
        )

    return {
        "get_id_servicio": get_id_servicio,
        "get_id_producto": get_id_producto,
        "crear_barbero": crear_barbero,
    }