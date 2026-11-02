"""Carga datos demo idempotentes. Uso: python -m scripts.seed_demo"""
import sqlite3
from datetime import timedelta, date
from pathlib import Path

from app import create_app
from app.data.db import init_schema
from app.domain import servicios as dom_svc
from app.domain import gastos as dom_gastos
from app.domain import inventario as dom_inv


def ya_existe(conn, table, seed_key):
    return conn.execute(
        f"SELECT 1 FROM {table} WHERE seed_key = ?", (seed_key,)
    ).fetchone() is not None


def upsert_catalogos(conn):
    sql = Path("app/data/seed_demo.sql").read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()


def seed_operaciones(conn):
    hoy = date.today()
    lunes = hoy - timedelta(days=hoy.weekday())

    servicios = {r["nombre"]: r["id"] for r in conn.execute(
        "SELECT id, nombre FROM servicios")}
    prod_by_codigo = {r["codigo_interno"]: r["id"] for r in conn.execute(
        "SELECT id, codigo_interno FROM productos WHERE codigo_interno IS NOT NULL")}

    def d(offset):
        return (lunes + timedelta(days=offset)).isoformat()

    CERA = prod_by_codigo["PROD-CERA"]
    SHAMP = prod_by_codigo["PROD-SHAMP"]
    ACEITE = prod_by_codigo["PROD-ACEITE"]

    ops = [
        ("compra",     "demo-c-1",  d(0), CERA,  10, "80.00"),
        ("compra",     "demo-c-2",  d(0), SHAMP, 20, "60.00"),
        ("compra",     "demo-c-3",  d(0), ACEITE, 8, "90.00"),
        ("venta_svc",  "demo-vs-1", d(0) + "T12:00:00", "Corte",         "100.00", "efectivo"),
        ("venta_svc",  "demo-vs-2", d(0) + "T13:00:00", "Barba",         "70.00",  "efectivo"),
        ("gasto",      "demo-g-1",  d(0), "Renta local (demo)", "renta", "800.00"),
        ("venta_svc",  "demo-vs-3", d(1) + "T11:00:00", "Corte + Barba", "150.00", "tarjeta"),
        ("venta_prod", "demo-vp-1", d(1), CERA,  2, "150.00"),
        ("venta_prod", "demo-vp-2", d(1), SHAMP, 3, "120.00"),
        ("compra",     "demo-c-4",  d(2), CERA,  5, "85.00"),
        ("gasto",      "demo-g-2",  d(2), "Luz (demo)", "servicios", "250.00"),
        ("venta_svc",  "demo-vs-4", d(3) + "T10:00:00", "Corte", "100.00", "efectivo"),
        ("venta_prod", "demo-vp-3", d(3), ACEITE, 2, "180.00"),
        ("ajuste",     "demo-aj-1", d(4), SHAMP, -1, "Merma por producto danado (demo)"),
    ]

    for op in ops:
        tipo, key = op[0], op[1]
        if tipo == "compra":
            if not ya_existe(conn, "compras_inventario", key):
                cid = dom_inv.registrar_compra(
                    conn, fecha=op[2], producto_id=op[3],
                    cantidad=op[4], costo_unitario=op[5],
                )
                conn.execute("UPDATE compras_inventario SET seed_key = ? WHERE id = ?", (key, cid))
                conn.commit()
        elif tipo == "venta_svc":
            if not ya_existe(conn, "ventas_servicio", key):
                vid = dom_svc.registrar_venta_servicio(
                    conn, servicio_id=servicios[op[3]], fecha_hora=op[2],
                    precio_cobrado=op[4], metodo_pago=op[5],
                )
                conn.execute("UPDATE ventas_servicio SET seed_key = ? WHERE id = ?", (key, vid))
                conn.commit()
        elif tipo == "gasto":
            if not ya_existe(conn, "gastos_operativos", key):
                gid = dom_gastos.registrar_gasto(
                    conn, fecha=op[2], descripcion=op[3],
                    categoria=op[4], importe=op[5], metodo_pago="efectivo",
                )
                conn.execute("UPDATE gastos_operativos SET seed_key = ? WHERE id = ?", (key, gid))
                conn.commit()
        elif tipo == "venta_prod":
            if not ya_existe(conn, "ventas_producto", key):
                vid = dom_inv.registrar_venta_producto(
                    conn, fecha=op[2], producto_id=op[3],
                    cantidad=op[4], precio_unitario=op[5],
                )
                conn.execute("UPDATE ventas_producto SET seed_key = ? WHERE id = ?", (key, vid))
                conn.commit()
        elif tipo == "ajuste":
            if not ya_existe(conn, "ajustes_inventario", key):
                dom_inv.registrar_ajuste(
                    conn, fecha=op[2], producto_id=op[3],
                    cantidad_delta=op[4], motivo=op[5],
                )
                conn.execute(
                    "UPDATE ajustes_inventario SET seed_key = ? "
                    "WHERE id = last_insert_rowid()", (key,))
                conn.commit()


def main():
    app = create_app()
    with app.app_context():
        init_schema(app.config["DATABASE"], app.config["SCHEMA_PATH"])
    with sqlite3.connect(app.config["DATABASE"]) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        upsert_catalogos(conn)
        seed_operaciones(conn)
    print(f"[OK] Datos demo cargados en {app.config['DATABASE']}")


if __name__ == "__main__":
    main()