"""Reporte por barbero (individual o global). Solo lee datos, no escribe."""
from decimal import Decimal, ROUND_HALF_UP

from ._rango import rango_exclusivo

CENT = Decimal("0.01")


def _q2(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _lista_barberos(conn, barbero_id=None):
    if barbero_id:
        return conn.execute(
            "SELECT id, nombre, comision_pct_default FROM barberos WHERE id = ?",
            (barbero_id,),
        ).fetchall()
    return conn.execute(
        "SELECT id, nombre, comision_pct_default FROM barberos "
        "WHERE activo = 1 ORDER BY nombre"
    ).fetchall()


def _detalle_servicios(conn, barbero_id, inicio, fin_excl):
    return conn.execute(
        """SELECT vs.id, vs.fecha_hora, vs.precio_cobrado,
                  vs.comision_pct, vs.comision_monto,
                  s.nombre AS servicio_nombre
           FROM ventas_servicio vs
           JOIN servicios s ON s.id = vs.servicio_id
           WHERE vs.estado = 'valida'
             AND vs.barbero_id = ?
             AND vs.fecha_hora >= ? AND vs.fecha_hora < ?
           ORDER BY vs.fecha_hora""",
        (barbero_id, inicio, fin_excl),
    ).fetchall()


def _detalle_productos(conn, barbero_id, inicio, fin_excl):
    return conn.execute(
        """SELECT vp.id, vp.fecha, vp.cantidad, vp.precio_unitario,
                  vp.total_venta, vp.comision_pct, vp.comision_monto,
                  p.nombre AS producto_nombre
           FROM ventas_producto vp
           JOIN productos p ON p.id = vp.producto_id
           WHERE vp.estado = 'valida'
             AND vp.barbero_id = ?
             AND vp.fecha >= ? AND vp.fecha < ?
           ORDER BY vp.fecha, vp.id""",
        (barbero_id, inicio, fin_excl),
    ).fetchall()


def calcular_reporte_barbero(conn, inicio_iso, fin_iso, barbero_id=None):
    """Reporte por barbero o consolidado de todos los barberos activos.

    Normaliza los límites para que funcionen con columnas DATE y DATETIME.
    """
    inicio, fin_excl = rango_exclusivo(inicio_iso, fin_iso)
    barberos = _lista_barberos(conn, barbero_id)
    resultado = []

    for b in barberos:
        svc = _detalle_servicios(conn, b["id"], inicio, fin_excl)
        prod = _detalle_productos(conn, b["id"], inicio, fin_excl)

        ing_svc = sum(
            (Decimal(r["precio_cobrado"]) for r in svc), Decimal("0")
        )
        com_svc = sum(
            (Decimal(r["comision_monto"] or "0") for r in svc), Decimal("0")
        )
        num_svc = len(svc)

        ing_prod = sum(
            (Decimal(r["total_venta"]) for r in prod), Decimal("0")
        )
        com_prod = sum(
            (Decimal(r["comision_monto"] or "0") for r in prod), Decimal("0")
        )
        num_prod = len(prod)

        resultado.append({
            "id": b["id"],
            "nombre": b["nombre"],
            "comision_pct_default": b["comision_pct_default"],
            "num_servicios": num_svc,
            "ingresos_svc": _q2(ing_svc),
            "comision_svc": _q2(com_svc),
            "num_ventas_prod": num_prod,
            "ingresos_prod": _q2(ing_prod),
            "comision_prod": _q2(com_prod),
            "comision_total": _q2(com_svc + com_prod),
            "detalle_servicios": svc,
            "detalle_productos": prod,
        })

    return resultado