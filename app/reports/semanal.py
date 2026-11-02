"""Reporte semanal con corte dominical. Solo lee datos, no escribe."""
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from .panel import calcular_panel

CENT = Decimal("0.01")


def _q2(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def rango_semana(fecha_ref_iso=None):
    """Devuelve (inicio_lunes_iso, fin_domingo_iso). Semana lunes->domingo."""
    if fecha_ref_iso:
        ref = date.fromisoformat(fecha_ref_iso)
    else:
        ref = date.today()
    lunes = ref - timedelta(days=ref.weekday())
    domingo = lunes + timedelta(days=6)
    return lunes.isoformat(), domingo.isoformat()


def rango_semana_anterior(fecha_ref_iso=None):
    """Devuelve (inicio, fin) de la semana anterior para comparacion."""
    lunes_iso, _ = rango_semana(fecha_ref_iso)
    lunes = date.fromisoformat(lunes_iso) - timedelta(days=7)
    domingo = lunes + timedelta(days=6)
    return lunes.isoformat(), domingo.isoformat()


def calcular_semanal(conn, fecha_ref_iso=None):
    """KPIs de la semana + comparacion con semana anterior + desglose por barbero."""
    lunes, domingo = rango_semana(fecha_ref_iso)
    inicio_iso = f"{lunes}T00:00:00"
    fin_iso = f"{domingo}T23:59:59"

    kpis_actual = calcular_panel(conn, inicio_iso, fin_iso)

    lunes_ant, domingo_ant = rango_semana_anterior(fecha_ref_iso)
    kpis_anterior = calcular_panel(
        conn,
        f"{lunes_ant}T00:00:00",
        f"{domingo_ant}T23:59:59",
    )

    barberos = conn.execute(
        """SELECT b.id, b.nombre,
                  COALESCE(SUM(CASE WHEN vs.estado = 'valida'
                                    THEN CAST(vs.precio_cobrado AS REAL) END), 0) AS ingresos_svc,
                  COALESCE(SUM(CASE WHEN vs.estado = 'valida'
                                    THEN CAST(vs.comision_monto AS REAL) END), 0) AS comision_svc,
                  COUNT(CASE WHEN vs.estado = 'valida' THEN 1 END) AS num_servicios
           FROM barberos b
           LEFT JOIN ventas_servicio vs
             ON vs.barbero_id = b.id
            AND vs.fecha_hora >= ? AND vs.fecha_hora < ?
           WHERE b.activo = 1
           GROUP BY b.id, b.nombre
           ORDER BY b.nombre""",
        (inicio_iso, fin_iso),
    ).fetchall()

    barberos_con_productos = []
    for b in barberos:
        prod_row = conn.execute(
            """SELECT COALESCE(SUM(CAST(total_venta AS REAL)), 0) AS ventas_prod,
                      COALESCE(SUM(CAST(comision_monto AS REAL)), 0) AS comision_prod,
                      COUNT(*) AS num_ventas
               FROM ventas_producto
               WHERE estado = 'valida'
                 AND barbero_id = ?
                 AND fecha >= ? AND fecha < ?""",
            (b["id"], lunes, domingo + "~"),
        ).fetchone()

        comision_svc = Decimal(str(b["comision_svc"] or 0))
        comision_prod = Decimal(str(prod_row["comision_prod"] or 0))

        barberos_con_productos.append({
            "id": b["id"],
            "nombre": b["nombre"],
            "num_servicios": b["num_servicios"],
            "ingresos_svc": _q2(Decimal(str(b["ingresos_svc"] or 0))),
            "comision_svc": _q2(comision_svc),
            "num_ventas_prod": prod_row["num_ventas"],
            "ventas_prod": _q2(Decimal(str(prod_row["ventas_prod"] or 0))),
            "comision_prod": _q2(comision_prod),
            "comision_total": _q2(comision_svc + comision_prod),
        })

    return {
        "lunes": lunes,
        "domingo": domingo,
        "lunes_anterior": lunes_ant,
        "domingo_anterior": domingo_ant,
        "kpis_actual": kpis_actual,
        "kpis_anterior": kpis_anterior,
        "por_barbero": barberos_con_productos,
    }