"""Reporte diario. Solo lee datos, no escribe."""
from decimal import Decimal, ROUND_HALF_UP

from .panel import calcular_panel

CENT = Decimal("0.01")


def _q2(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def calcular_diario(conn, fecha_iso):
    """Devuelve KPIs del día + listas detalladas para mostrar."""
    inicio = f"{fecha_iso}T00:00:00"
    fin = f"{fecha_iso}T23:59:59"

    kpis = calcular_panel(conn, inicio, fin)

    servicios = conn.execute(
        """SELECT vs.id, vs.fecha_hora, vs.precio_cobrado, vs.metodo_pago,
                  vs.comision_pct, vs.comision_monto,
                  s.nombre AS servicio_nombre,
                  b.nombre AS barbero_nombre
           FROM ventas_servicio vs
           JOIN servicios s ON s.id = vs.servicio_id
           LEFT JOIN barberos b ON b.id = vs.barbero_id
           WHERE vs.estado = 'valida'
             AND vs.fecha_hora >= ? AND vs.fecha_hora < ?
           ORDER BY vs.fecha_hora""",
        (inicio, fin),
    ).fetchall()

    ventas_prod = conn.execute(
        """SELECT vp.id, vp.fecha, vp.cantidad, vp.precio_unitario,
                  vp.total_venta, vp.costo_total_snapshot,
                  vp.comision_pct, vp.comision_monto,
                  p.nombre AS producto_nombre,
                  b.nombre AS barbero_nombre
           FROM ventas_producto vp
           JOIN productos p ON p.id = vp.producto_id
           LEFT JOIN barberos b ON b.id = vp.barbero_id
           WHERE vp.estado = 'valida'
             AND vp.fecha >= ? AND vp.fecha < ?
           ORDER BY vp.fecha, vp.id""",
        (fecha_iso, fecha_iso + "~"),
    ).fetchall()

    gastos = conn.execute(
        """SELECT id, fecha, descripcion, categoria, importe, metodo_pago
           FROM gastos_operativos
           WHERE estado = 'valida'
             AND fecha >= ? AND fecha < ?
           ORDER BY fecha, id""",
        (fecha_iso, fecha_iso + "~"),
    ).fetchall()

    compras = conn.execute(
        """SELECT c.id, c.fecha, c.cantidad, c.costo_unitario, c.total,
                  p.nombre AS producto_nombre
           FROM compras_inventario c
           JOIN productos p ON p.id = c.producto_id
           WHERE c.estado = 'valida'
             AND c.fecha >= ? AND c.fecha < ?
           ORDER BY c.fecha, c.id""",
        (fecha_iso, fecha_iso + "~"),
    ).fetchall()

    return {
        "fecha": fecha_iso,
        "kpis": kpis,
        "servicios": servicios,
        "ventas_producto": ventas_prod,
        "gastos": gastos,
        "compras": compras,
    }