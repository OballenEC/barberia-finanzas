"""Pruebas de persistencia: los datos sobreviven a reiniciar la app."""
import gc
import shutil
import sqlite3
import tempfile
from pathlib import Path

from app.data.db import init_schema
from app.domain import servicios as dom_svc

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = BASE_DIR / "app" / "data" / "schema.sql"


def _abrir(db_path):
    c = sqlite3.connect(db_path)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    return c


def _cleanup(tmpdir):
    """En Windows los handles de SQLite pueden tardar en liberarse.
    Forzamos GC y reintentamos; si sigue fallando, ignoramos (es un temp)."""
    gc.collect()
    try:
        shutil.rmtree(tmpdir, ignore_errors=True)
    except Exception:
        pass


def test_datos_persisten_entre_conexiones():
    """Registrar una venta, cerrar la conexión, abrir otra y comprobar que sigue."""
    tmpdir = tempfile.mkdtemp(prefix="barberia_test_")
    db_path = str(Path(tmpdir) / "test.sqlite3")

    try:
        # Primera conexión: crear schema, insertar servicio y venta
        init_schema(db_path, str(SCHEMA_PATH))
        c1 = _abrir(db_path)
        c1.execute(
            "INSERT INTO servicios (nombre, precio_sugerido, activo) "
            "VALUES ('Corte', '100.00', 1)"
        )
        sid = c1.execute(
            "SELECT id FROM servicios WHERE nombre = 'Corte'"
        ).fetchone()["id"]
        c1.commit()
        vid = dom_svc.registrar_venta_servicio(
            c1, servicio_id=sid, fecha_hora="2026-11-02T10:00:00",
            precio_cobrado="100.00", metodo_pago="efectivo",
        )
        c1.close()

        # Segunda conexión (simula reinicio de la app)
        c2 = _abrir(db_path)
        row = c2.execute(
            "SELECT * FROM ventas_servicio WHERE id = ?", (vid,)
        ).fetchone()
        assert row is not None
        assert row["precio_cobrado"] == "100.00"
        assert row["estado"] == "valida"
        c2.close()
    finally:
        _cleanup(tmpdir)


def test_seed_idempotente_no_duplica():
    """Ejecutar init_schema dos veces no duplica tablas ni datos."""
    tmpdir = tempfile.mkdtemp(prefix="barberia_test_")
    db_path = str(Path(tmpdir) / "test.sqlite3")

    try:
        init_schema(db_path, str(SCHEMA_PATH))
        init_schema(db_path, str(SCHEMA_PATH))

        c = _abrir(db_path)

        tablas = c.execute(
            "SELECT COUNT(*) FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        ).fetchone()[0]
        assert tablas == 9, f"Esperaba 9 tablas, hay {tablas}"

        c.execute(
            "INSERT OR IGNORE INTO servicios (nombre, precio_sugerido, activo) "
            "VALUES ('Corte', '100.00', 1)"
        )
        c.execute(
            "INSERT OR IGNORE INTO servicios (nombre, precio_sugerido, activo) "
            "VALUES ('Corte', '100.00', 1)"
        )
        c.commit()

        count = c.execute(
            "SELECT COUNT(*) FROM servicios WHERE nombre = 'Corte'"
        ).fetchone()[0]
        assert count == 1, f"Esperaba 1 'Corte', hay {count}"

        c.close()
    finally:
        _cleanup(tmpdir)