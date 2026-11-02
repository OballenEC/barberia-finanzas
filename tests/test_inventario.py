"""Pruebas del motor de inventario: CPM, ventas, anulaciones."""
import pytest

from app.domain import inventario as dom_inv


def _stock(conn, producto_id):
    return conn.execute(
        "SELECT stock_actual, costo_promedio FROM productos WHERE id = ?",
        (producto_id,),
    ).fetchone()


def test_compra_aumenta_stock_y_cpm(conn, helpers):
    """10 uds a $80 = stock 10, CPM $80."""
    pid = helpers["get_id_producto"]("PROD-CERA")
    dom_inv.registrar_compra(
        conn, fecha="2026-11-02", producto_id=pid,
        cantidad=10, costo_unitario="80.00",
    )
    p = _stock(conn, pid)
    assert p["stock_actual"] == 10
    assert p["costo_promedio"] == "80.00"


def test_segunda_compra_recalcula_cpm_ponderado(conn, helpers):
    """10@$80 + 10@$100 = 20 uds, CPM $90."""
    pid = helpers["get_id_producto"]("PROD-CERA")
    dom_inv.registrar_compra(
        conn, fecha="2026-11-02", producto_id=pid,
        cantidad=10, costo_unitario="80.00",
    )
    dom_inv.registrar_compra(
        conn, fecha="2026-11-03", producto_id=pid,
        cantidad=10, costo_unitario="100.00",
    )
    p = _stock(conn, pid)
    assert p["stock_actual"] == 20
    assert p["costo_promedio"] == "90.00"


def test_venta_descuenta_stock_y_congela_snapshot(conn, helpers):
    """Venta congela el CPM del momento en la fila."""
    pid = helpers["get_id_producto"]("PROD-CERA")
    dom_inv.registrar_compra(
        conn, fecha="2026-11-02", producto_id=pid,
        cantidad=10, costo_unitario="80.00",
    )
    vid = dom_inv.registrar_venta_producto(
        conn, fecha="2026-11-02", producto_id=pid,
        cantidad=2, precio_unitario="150.00",
    )
    venta = conn.execute(
        "SELECT * FROM ventas_producto WHERE id = ?", (vid,)
    ).fetchone()
    assert venta["costo_unitario_snapshot"] == "80.00"
    assert venta["costo_total_snapshot"] == "160.00"
    assert venta["total_venta"] == "300.00"

    p = _stock(conn, pid)
    assert p["stock_actual"] == 8
    assert p["costo_promedio"] == "80.00"  # CPM no cambia al vender


def test_snapshot_inmutable_a_compras_futuras(conn, helpers):
    """Comprar más caro después NO altera el snapshot de una venta previa."""
    pid = helpers["get_id_producto"]("PROD-CERA")
    dom_inv.registrar_compra(
        conn, fecha="2026-11-02", producto_id=pid,
        cantidad=10, costo_unitario="80.00",
    )
    vid = dom_inv.registrar_venta_producto(
        conn, fecha="2026-11-02", producto_id=pid,
        cantidad=2, precio_unitario="150.00",
    )
    # Compra posterior más cara
    dom_inv.registrar_compra(
        conn, fecha="2026-11-03", producto_id=pid,
        cantidad=10, costo_unitario="100.00",
    )
    venta = conn.execute(
        "SELECT * FROM ventas_producto WHERE id = ?", (vid,)
    ).fetchone()
    # El snapshot NO cambia
    assert venta["costo_unitario_snapshot"] == "80.00"
    assert venta["costo_total_snapshot"] == "160.00"


def test_venta_sin_stock_falla(conn, helpers):
    pid = helpers["get_id_producto"]("PROD-CERA")
    dom_inv.registrar_compra(
        conn, fecha="2026-11-02", producto_id=pid,
        cantidad=5, costo_unitario="80.00",
    )
    with pytest.raises(ValueError, match="Stock insuficiente"):
        dom_inv.registrar_venta_producto(
            conn, fecha="2026-11-02", producto_id=pid,
            cantidad=10, precio_unitario="150.00",
        )


def test_anular_compra_con_venta_posterior_bloqueado(conn, helpers):
    """La regla clave del MVP: no anular compra si hay ventas después."""
    pid = helpers["get_id_producto"]("PROD-CERA")
    cid = dom_inv.registrar_compra(
        conn, fecha="2026-11-02", producto_id=pid,
        cantidad=10, costo_unitario="80.00",
    )
    dom_inv.registrar_venta_producto(
        conn, fecha="2026-11-03", producto_id=pid,
        cantidad=2, precio_unitario="150.00",
    )
    with pytest.raises(ValueError, match="ventas posteriores"):
        dom_inv.anular_compra(conn, compra_id=cid, motivo="prueba")


def test_anular_venta_reintegra_stock(conn, helpers):
    pid = helpers["get_id_producto"]("PROD-CERA")
    dom_inv.registrar_compra(
        conn, fecha="2026-11-02", producto_id=pid,
        cantidad=10, costo_unitario="80.00",
    )
    vid = dom_inv.registrar_venta_producto(
        conn, fecha="2026-11-02", producto_id=pid,
        cantidad=3, precio_unitario="150.00",
    )
    assert _stock(conn, pid)["stock_actual"] == 7

    dom_inv.anular_venta_producto(conn, venta_id=vid, motivo="cliente devolvió")
    assert _stock(conn, pid)["stock_actual"] == 10