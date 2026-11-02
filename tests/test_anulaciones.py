"""Pruebas de anulaciones auditables: nada se borra, todo queda en historial."""
import pytest

from app.domain import barberos as dom_barberos
from app.domain import gastos as dom_gastos
from app.domain import inventario as dom_inv
from app.domain import servicios as dom_svc
from app.reports.panel import calcular_panel


def test_anular_servicio_lo_excluye_de_totales(conn, helpers):
    """Un servicio anulado no suma al panel pero SÍ queda en historial."""
    bid = dom_barberos.crear_barbero(conn, nombre="Luis", comision_pct_default="35.00")
    sid = helpers["get_id_servicio"]("Corte")
    vid = dom_svc.registrar_venta_servicio(
        conn, servicio_id=sid, fecha_hora="2026-11-02T10:00:00",
        precio_cobrado="100.00", metodo_pago="efectivo", barbero_id=bid,
    )
    kpis_antes = calcular_panel(conn, "2026-11-02", "2026-11-08")
    assert kpis_antes["ingresos_servicios"] == 100

    dom_svc.anular_venta_servicio(conn, venta_id=vid, motivo="error de captura")

    kpis_despues = calcular_panel(conn, "2026-11-02", "2026-11-08")
    assert kpis_despues["ingresos_servicios"] == 0
    assert kpis_despues["comisiones_servicios"] == 0

    # El historial sigue ahí
    row = conn.execute(
        "SELECT * FROM ventas_servicio WHERE id = ?", (vid,)
    ).fetchone()
    assert row["estado"] == "anulada"
    assert row["motivo_anulacion"] == "error de captura"


def test_anular_gasto_lo_excluye_de_totales(conn):
    gid = dom_gastos.registrar_gasto(
        conn, fecha="2026-11-02", descripcion="Renta",
        categoria="renta", importe="800.00", metodo_pago="efectivo",
    )
    kpis_antes = calcular_panel(conn, "2026-11-02", "2026-11-08")
    assert kpis_antes["gastos_operativos"] == 800

    dom_gastos.anular_gasto(conn, gasto_id=gid, motivo="duplicado")

    kpis_despues = calcular_panel(conn, "2026-11-02", "2026-11-08")
    assert kpis_despues["gastos_operativos"] == 0

    # Historial
    row = conn.execute(
        "SELECT * FROM gastos_operativos WHERE id = ?", (gid,)
    ).fetchone()
    assert row["estado"] == "anulada"


def test_anular_venta_producto_reintegra_stock_y_excluye_cogs(conn, helpers):
    """Anular una venta devuelve stock Y quita el COGS del reporte."""
    pid = helpers["get_id_producto"]("PROD-CERA")
    dom_inv.registrar_compra(
        conn, fecha="2026-11-02", producto_id=pid,
        cantidad=10, costo_unitario="80.00",
    )
    vid = dom_inv.registrar_venta_producto(
        conn, fecha="2026-11-02", producto_id=pid,
        cantidad=2, precio_unitario="150.00",
    )

    # Antes: stock 8, COGS 160
    kpis_antes = calcular_panel(conn, "2026-11-02", "2026-11-08")
    assert kpis_antes["cogs"] == 160
    assert conn.execute(
        "SELECT stock_actual FROM productos WHERE id = ?", (pid,)
    ).fetchone()["stock_actual"] == 8

    dom_inv.anular_venta_producto(conn, venta_id=vid, motivo="devolución")

    # Después: stock 10, COGS 0
    kpis_despues = calcular_panel(conn, "2026-11-02", "2026-11-08")
    assert kpis_despues["cogs"] == 0
    assert kpis_despues["ventas_productos"] == 0
    assert conn.execute(
        "SELECT stock_actual FROM productos WHERE id = ?", (pid,)
    ).fetchone()["stock_actual"] == 10


def test_anular_dos_veces_falla(conn, helpers):
    """La segunda anulación debe fallar; no se permite anular dos veces."""
    sid = helpers["get_id_servicio"]("Corte")
    vid = dom_svc.registrar_venta_servicio(
        conn, servicio_id=sid, fecha_hora="2026-11-02T10:00:00",
        precio_cobrado="100.00", metodo_pago="efectivo",
    )
    dom_svc.anular_venta_servicio(conn, venta_id=vid, motivo="primera")

    with pytest.raises(ValueError, match="ya está anulada"):
        dom_svc.anular_venta_servicio(conn, venta_id=vid, motivo="segunda")


def test_anular_sin_motivo_falla_en_todos_los_modulos(conn, helpers):
    """Motivo vacío debe ser rechazado en servicios, gastos, compras y ventas."""
    sid = helpers["get_id_servicio"]("Corte")
    vid_svc = dom_svc.registrar_venta_servicio(
        conn, servicio_id=sid, fecha_hora="2026-11-02T10:00:00",
        precio_cobrado="100.00", metodo_pago="efectivo",
    )
    with pytest.raises(ValueError, match="motivo"):
        dom_svc.anular_venta_servicio(conn, venta_id=vid_svc, motivo="")

    gid = dom_gastos.registrar_gasto(
        conn, fecha="2026-11-02", descripcion="X", categoria="otro",
        importe="50.00", metodo_pago="efectivo",
    )
    with pytest.raises(ValueError, match="motivo"):
        dom_gastos.anular_gasto(conn, gasto_id=gid, motivo="   ")