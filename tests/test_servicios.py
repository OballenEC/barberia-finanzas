"""Pruebas de servicios + comisiones."""
import pytest

from app.domain import servicios as dom_svc


def test_registrar_servicio_sin_barbero(conn, helpers):
    """Un servicio sin barbero no genera comisión."""
    sid = helpers["get_id_servicio"]("Corte")
    vid = dom_svc.registrar_venta_servicio(
        conn,
        servicio_id=sid,
        fecha_hora="2026-11-02T10:00:00",
        precio_cobrado="100.00",
        metodo_pago="efectivo",
        barbero_id=None,
    )
    row = conn.execute(
        "SELECT * FROM ventas_servicio WHERE id = ?", (vid,)
    ).fetchone()
    assert row["precio_cobrado"] == "100.00"
    assert row["barbero_id"] is None
    assert row["comision_pct"] is None
    assert row["comision_monto"] is None
    assert row["estado"] == "valida"


def test_registrar_servicio_con_barbero_default(conn, helpers):
    """Un servicio con barbero usa el % default del barbero."""
    bid = helpers["crear_barbero"]("Luis", "35.00")
    sid = helpers["get_id_servicio"]("Corte")
    vid = dom_svc.registrar_venta_servicio(
        conn,
        servicio_id=sid,
        fecha_hora="2026-11-02T10:00:00",
        precio_cobrado="100.00",
        metodo_pago="efectivo",
        barbero_id=bid,
    )
    row = conn.execute(
        "SELECT * FROM ventas_servicio WHERE id = ?", (vid,)
    ).fetchone()
    assert row["barbero_id"] == bid
    assert row["comision_pct"] == "35.00"
    assert row["comision_monto"] == "35.00"  # 100 * 0.35


def test_registrar_servicio_con_override_pct(conn, helpers):
    """El override sobreescribe el default del barbero."""
    bid = helpers["crear_barbero"]("Juan", "35.00")
    sid = helpers["get_id_servicio"]("Corte + Barba")
    vid = dom_svc.registrar_venta_servicio(
        conn,
        servicio_id=sid,
        fecha_hora="2026-11-02T11:00:00",
        precio_cobrado="150.00",
        metodo_pago="tarjeta",
        barbero_id=bid,
        comision_pct_override="40.00",
    )
    row = conn.execute(
        "SELECT * FROM ventas_servicio WHERE id = ?", (vid,)
    ).fetchone()
    assert row["comision_pct"] == "40.00"
    assert row["comision_monto"] == "60.00"  # 150 * 0.40


def test_comision_redondeo_correcto(conn, helpers):
    """$33.33 al 35% = $11.6655 → redondea a $11.67 (HALF_UP)."""
    bid = helpers["crear_barbero"]("Test", "35.00")
    sid = helpers["get_id_servicio"]("Corte")
    vid = dom_svc.registrar_venta_servicio(
        conn,
        servicio_id=sid,
        fecha_hora="2026-11-02T12:00:00",
        precio_cobrado="33.33",
        metodo_pago="efectivo",
        barbero_id=bid,
    )
    row = conn.execute(
        "SELECT * FROM ventas_servicio WHERE id = ?", (vid,)
    ).fetchone()
    assert row["comision_monto"] == "11.67"


def test_precio_negativo_rechazado(conn, helpers):
    sid = helpers["get_id_servicio"]("Corte")
    with pytest.raises(ValueError):
        dom_svc.registrar_venta_servicio(
            conn,
            servicio_id=sid,
            fecha_hora="2026-11-02T10:00:00",
            precio_cobrado="-50.00",
            metodo_pago="efectivo",
        )


def test_anular_venta_servicio(conn, helpers):
    sid = helpers["get_id_servicio"]("Corte")
    vid = dom_svc.registrar_venta_servicio(
        conn,
        servicio_id=sid,
        fecha_hora="2026-11-02T10:00:00",
        precio_cobrado="100.00",
        metodo_pago="efectivo",
    )
    dom_svc.anular_venta_servicio(conn, venta_id=vid, motivo="prueba")
    row = conn.execute(
        "SELECT * FROM ventas_servicio WHERE id = ?", (vid,)
    ).fetchone()
    assert row["estado"] == "anulada"
    assert row["motivo_anulacion"] == "prueba"

    # Anular de nuevo debe fallar
    with pytest.raises(ValueError, match="ya está anulada"):
        dom_svc.anular_venta_servicio(conn, venta_id=vid, motivo="otra")


def test_anular_sin_motivo_falla(conn, helpers):
    sid = helpers["get_id_servicio"]("Corte")
    vid = dom_svc.registrar_venta_servicio(
        conn,
        servicio_id=sid,
        fecha_hora="2026-11-02T10:00:00",
        precio_cobrado="100.00",
        metodo_pago="efectivo",
    )
    with pytest.raises(ValueError, match="motivo"):
        dom_svc.anular_venta_servicio(conn, venta_id=vid, motivo="")