"""Pruebas de reportes: panel, diario, semanal, por barbero.

Estas pruebas verifican las fórmulas financieras del proyecto:
- Anti-doble-conteo (compras NO restan del resultado)
- Separación entre ingresos/ventas/gastos/compras/COGS/comisiones
- Resultado neto = ingresos + ventas - COGS - gastos - comisiones
- Flujo de efectivo separado del resultado
"""
from decimal import Decimal

from app.domain import barberos as dom_barberos
from app.domain import gastos as dom_gastos
from app.domain import inventario as dom_inv
from app.domain import servicios as dom_svc
from app.reports.panel import calcular_panel
from app.reports.diario import calcular_diario
from app.reports.semanal import calcular_semanal
from app.reports.barbero import calcular_reporte_barbero


def _setup_escenario_completo(conn):
    """Escenario con 1 barbero, 1 servicio, 1 producto comprado y vendido,
    y 1 gasto. Todos con fechas dentro de la misma semana."""
    # Barbero Luis al 35%
    bid = dom_barberos.crear_barbero(conn, nombre="Luis", comision_pct_default="35.00")

    # Servicio: Corte $100 por Luis → comisión $35
    sid = conn.execute(
        "SELECT id FROM servicios WHERE nombre = 'Corte'"
    ).fetchone()["id"]
    dom_svc.registrar_venta_servicio(
        conn,
        servicio_id=sid,
        fecha_hora="2026-11-02T10:00:00",
        precio_cobrado="100.00",
        metodo_pago="efectivo",
        barbero_id=bid,
    )

    # Compra: 10 ceras a $80 (NO debe restar del resultado)
    pid = conn.execute(
        "SELECT id FROM productos WHERE codigo_interno = 'PROD-CERA'"
    ).fetchone()["id"]
    dom_inv.registrar_compra(
        conn, fecha="2026-11-02", producto_id=pid,
        cantidad=10, costo_unitario="80.00",
    )

    # Venta: 2 ceras a $150 (COGS = 2*80 = $160, comisión 35% de $300 = $105)
    dom_inv.registrar_venta_producto(
        conn, fecha="2026-11-03", producto_id=pid,
        cantidad=2, precio_unitario="150.00",
    )
    # Atribuir la venta a Luis (la venta no lo asigna por defecto)
    conn.execute(
        "UPDATE ventas_producto SET barbero_id = ?, comision_pct = '35.00', "
        "comision_monto = '105.00' WHERE barbero_id IS NULL",
        (bid,),
    )
    conn.commit()

    # Gasto: $250 luz
    dom_gastos.registrar_gasto(
        conn, fecha="2026-11-04",
        descripcion="Luz", categoria="servicios",
        importe="250.00", metodo_pago="efectivo",
    )

    return {"barbero_id": bid, "producto_id": pid}


def test_panel_formulas_completas(conn):
    """Valida todas las fórmulas del panel con un escenario conocido."""
    _setup_escenario_completo(conn)

    kpis = calcular_panel(conn, "2026-11-02", "2026-11-08")

    # Ingresos/ventas/gastos/compras
    assert kpis["ingresos_servicios"] == Decimal("100.00")
    assert kpis["ventas_productos"] == Decimal("300.00")
    assert kpis["gastos_operativos"] == Decimal("250.00")
    assert kpis["compras_inventario"] == Decimal("800.00")
    assert kpis["cogs"] == Decimal("160.00")

    # Margen bruto = ventas - COGS = 300 - 160 = 140
    assert kpis["margen_bruto_productos"] == Decimal("140.00")

    # Comisiones
    assert kpis["comisiones_servicios"] == Decimal("35.00")
    assert kpis["comisiones_productos"] == Decimal("105.00")
    assert kpis["comisiones_total"] == Decimal("140.00")

    # Resultado neto:
    # 100 + 300 - 160 - 250 - 35 - 105 = -150
    assert kpis["resultado_neto_estimado"] == Decimal("-150.00")

    # Flujo de efectivo: 100 + 300 - 250 - 800 - 35 - 105 = -790
    # (SÍ resta compras porque es flujo, no resultado)
    assert kpis["flujo_efectivo_estimado"] == Decimal("-790.00")


def test_anti_doble_conteo_compras_no_restan_del_resultado(conn):
    """Regla clave: comprar $800 en mercancía NO baja el resultado $800.

    Solo baja el COGS de las unidades efectivamente vendidas ($160).
    """
    _setup_escenario_completo(conn)
    kpis = calcular_panel(conn, "2026-11-02", "2026-11-08")

    # Si las compras restaran del resultado, este sería mucho más negativo.
    # Verificamos que el resultado NO incluye los $800 de compra.
    # Resultado sin compras: 100 + 300 - 160 - 250 - 35 - 105 = -150
    # Si compras restaran: -150 - 800 = -950 (sería incorrecto)
    assert kpis["resultado_neto_estimado"] == Decimal("-150.00")
    assert kpis["resultado_neto_estimado"] != Decimal("-950.00")


def test_reporte_diario_respeta_rango(conn):
    """El reporte diario solo incluye operaciones del día exacto."""
    _setup_escenario_completo(conn)

    # Día 1: solo el servicio y la compra
    dia2 = calcular_diario(conn, "2026-11-02")
    assert dia2["kpis"]["ingresos_servicios"] == Decimal("100.00")
    assert dia2["kpis"]["ventas_productos"] == Decimal("0.00")

    # Día 2: solo la venta de producto
    dia3 = calcular_diario(conn, "2026-11-03")
    assert dia3["kpis"]["ingresos_servicios"] == Decimal("0.00")
    assert dia3["kpis"]["ventas_productos"] == Decimal("300.00")


def test_reporte_semanal_compara_semana_anterior(conn):
    """La semana actual tiene datos; la anterior está en cero."""
    _setup_escenario_completo(conn)
    data = calcular_semanal(conn, "2026-11-02")

    # Semana actual
    assert data["kpis_actual"]["ingresos_servicios"] == Decimal("100.00")
    assert data["kpis_actual"]["ventas_productos"] == Decimal("300.00")

    # Semana anterior (vacía)
    assert data["kpis_anterior"]["ingresos_servicios"] == Decimal("0.00")
    assert data["kpis_anterior"]["ventas_productos"] == Decimal("0.00")


def test_reporte_barbero_agrega_servicios_y_productos(conn):
    """El reporte por barbero suma servicios + ventas de producto."""
    ids = _setup_escenario_completo(conn)

    filas = calcular_reporte_barbero(conn, "2026-11-02", "2026-11-08")
    assert len(filas) == 1
    luis = filas[0]

    assert luis["nombre"] == "Luis"
    assert luis["num_servicios"] == 1
    assert luis["ingresos_svc"] == Decimal("100.00")
    assert luis["comision_svc"] == Decimal("35.00")

    assert luis["num_ventas_prod"] == 1
    assert luis["ingresos_prod"] == Decimal("300.00")
    assert luis["comision_prod"] == Decimal("105.00")

    assert luis["comision_total"] == Decimal("140.00")


def test_reporte_barbero_filtra_por_id(conn):
    """Si pides un barbero específico, no te devuelve los demás."""
    _setup_escenario_completo(conn)
    otro = dom_barberos.crear_barbero(conn, nombre="Juan", comision_pct_default="40.00")

    filas_todos = calcular_reporte_barbero(conn, "2026-11-02", "2026-11-08")
    assert len(filas_todos) == 2

    filas_juan = calcular_reporte_barbero(
        conn, "2026-11-02", "2026-11-08", barbero_id=otro
    )
    assert len(filas_juan) == 1
    assert filas_juan[0]["nombre"] == "Juan"
    assert filas_juan[0]["num_servicios"] == 0  # Juan no trabajó