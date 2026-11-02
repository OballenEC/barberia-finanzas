"""KPIs del panel principal. Solo lee datos, no escribe."""
from decimal import Decimal, ROUND_HALF_UP

from ._rango import rango_exclusivo

CENT = Decimal("0.01")


def _sum_svc(conn, inicio_iso, fin_iso):
    row = conn.execute(
        """SELECT COALESCE(SUM(CAST(precio_cobrado AS REAL)), 0) AS ingresos,
                  COALESCE(SUM(CAST(comision_monto AS REAL)), 0) AS comisiones
           FROM ventas_servicio
           WHERE estado = 'valida'
             AND fecha_hora >= ? AND fecha_hora < ?""",
        (inicio_iso, fin_iso),
    ).fetchone()
    return Decimal(str(row["ingresos"])), Decimal(str(row["comisiones"]))


def _sum_prod(conn, inicio_iso, fin_iso):
    row = conn.execute(
        """SELECT COALESCE(SUM(CAST(total_venta AS REAL)), 0) AS ventas,
                  COALESCE(SUM(CAST(costo_total_snapshot AS REAL)), 0) AS cogs,
                  COALESCE(SUM(CAST(comision_monto AS REAL)), 0) AS comisiones
           FROM ventas_producto
           WHERE estado = 'valida'
             AND fecha >= ? AND fecha < ?""",
        (inicio_iso, fin_iso),
    ).fetchone()
    return (Decimal(str(row["ventas"])),
            Decimal(str(row["cogs"])),
            Decimal(str(row["comisiones"])))


def _sum_gastos(conn, inicio_iso, fin_iso):
    row = conn.execute(
        """SELECT COALESCE(SUM(CAST(importe AS REAL)), 0) AS total
           FROM gastos_operativos
           WHERE estado = 'valida'
             AND fecha >= ? AND fecha < ?""",
        (inicio_iso, fin_iso),
    ).fetchone()
    return Decimal(str(row["total"]))


def _sum_compras(conn, inicio_iso, fin_iso):
    row = conn.execute(
        """SELECT COALESCE(SUM(CAST(total AS REAL)), 0) AS total
           FROM compras_inventario
           WHERE estado = 'valida'
             AND fecha >= ? AND fecha < ?""",
        (inicio_iso, fin_iso),
    ).fetchone()
    return Decimal(str(row["total"]))


def _q2(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def calcular_panel(conn, inicio_iso, fin_iso):
    """Devuelve dict con todos los KPIs del panel.

    Normaliza los límites para que funcionen con columnas DATE y DATETIME.
    inicio_iso y fin_iso pueden llegar con formato 'YYYY-MM-DD' o
    'YYYY-MM-DDTHH:MM:SS'.
    """
    inicio, fin_excl = rango_exclusivo(inicio_iso, fin_iso)

    svc_ing, svc_com = _sum_svc(conn, inicio, fin_excl)
    prod_ventas, prod_cogs, prod_com = _sum_prod(conn, inicio, fin_excl)
    gastos = _sum_gastos(conn, inicio, fin_excl)
    compras = _sum_compras(conn, inicio, fin_excl)

    margen_bruto_prod = _q2(prod_ventas - prod_cogs)
    resultado_neto = _q2(
        svc_ing + prod_ventas - prod_cogs - gastos - svc_com - prod_com
    )
    flujo = _q2(svc_ing + prod_ventas - gastos - compras - svc_com - prod_com)

    return {
        "ingresos_servicios": _q2(svc_ing),
        "ventas_productos": _q2(prod_ventas),
        "gastos_operativos": _q2(gastos),
        "compras_inventario": _q2(compras),
        "cogs": _q2(prod_cogs),
        "margen_bruto_productos": margen_bruto_prod,
        "comisiones_servicios": _q2(svc_com),
        "comisiones_productos": _q2(prod_com),
        "comisiones_total": _q2(svc_com + prod_com),
        "resultado_neto_estimado": resultado_neto,
        "flujo_efectivo_estimado": flujo,
    }