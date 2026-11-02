from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from .money import parse_money, parse_positive_int, fmt
from app.data.repositories import (
    productos_repo, inventario_repo, ventas_producto_repo,
)

CENT = Decimal("0.01")


def _replay_cpm(conn, producto_id):
    """Recalcula stock_actual y costo_promedio desde las tablas origen.
    Solo considera operaciones con estado='valida'."""
    eventos = []

    for c in conn.execute(
        "SELECT fecha, id, cantidad, costo_unitario FROM compras_inventario "
        "WHERE producto_id = ? AND estado = 'valida'",
        (producto_id,),
    ):
        eventos.append((c["fecha"], 0, c["id"], "compra",
                        c["cantidad"], Decimal(c["costo_unitario"])))

    for v in conn.execute(
        "SELECT fecha, id, cantidad, costo_unitario_snapshot FROM ventas_producto "
        "WHERE producto_id = ? AND estado = 'valida'",
        (producto_id,),
    ):
        eventos.append((v["fecha"], 1, v["id"], "venta",
                        v["cantidad"], Decimal(v["costo_unitario_snapshot"])))

    for a in conn.execute(
        "SELECT fecha, id, cantidad_delta FROM ajustes_inventario "
        "WHERE producto_id = ?",
        (producto_id,),
    ):
        delta = a["cantidad_delta"]
        tipo = "ajuste_positivo" if delta > 0 else "ajuste_negativo"
        eventos.append((a["fecha"], 2, a["id"], tipo,
                        abs(delta), Decimal("0")))

    eventos.sort(key=lambda e: (e[0], e[1], e[2]))

    stock = 0
    cpm = Decimal("0")
    for _fecha, _prio, _id, tipo, qty, costo in eventos:
        if tipo == "compra":
            nuevo = stock + qty
            if nuevo > 0:
                cpm = ((Decimal(stock) * cpm + Decimal(qty) * costo)
                       / Decimal(nuevo)).quantize(CENT, rounding=ROUND_HALF_UP)
            stock = nuevo
        elif tipo == "ajuste_positivo":
            stock += qty
        else:
            stock -= qty

    conn.execute(
        "UPDATE productos SET stock_actual = ?, costo_promedio = ? WHERE id = ?",
        (stock, str(cpm), producto_id),
    )


def registrar_compra(conn, *, fecha, producto_id, cantidad, costo_unitario):
    prod = productos_repo.get_producto(conn, producto_id)
    if not prod:
        raise ValueError("Producto no encontrado")
    if not prod["activo"]:
        raise ValueError("El producto está inactivo")
    qty = parse_positive_int(cantidad, field="cantidad")
    costo = parse_money(costo_unitario, field="costo unitario")
    if costo == 0:
        raise ValueError("El costo unitario debe ser mayor que cero")
    total = (costo * qty).quantize(CENT, rounding=ROUND_HALF_UP)
    creado_en = datetime.now().isoformat(timespec="seconds")

    with conn:
        compra_id = inventario_repo.insert_compra(
            conn,
            fecha=fecha, producto_id=producto_id, cantidad=qty,
            costo_unitario=fmt(costo), total=fmt(total), creado_en=creado_en,
        )
        _replay_cpm(conn, producto_id)
    return compra_id


def anular_compra(conn, *, compra_id, motivo):
    if not motivo or not motivo.strip():
        raise ValueError("El motivo es obligatorio")
    compra = inventario_repo.get_compra(conn, compra_id)
    if not compra:
        raise ValueError("Compra no encontrada")
    if compra["estado"] != "valida":
        raise ValueError("La compra ya está anulada")

    ventas_post = conn.execute(
        "SELECT COUNT(*) FROM ventas_producto "
        "WHERE producto_id = ? AND estado = 'valida' AND fecha > ?",
        (compra["producto_id"], compra["fecha"]),
    ).fetchone()[0]
    if ventas_post > 0:
        raise ValueError(
            "No se puede anular: existen ventas posteriores de este producto. "
            "Usa un ajuste de inventario para corregir el stock."
        )

    with conn:
        inventario_repo.marcar_compra_anulada(conn, compra_id, motivo.strip())
        _replay_cpm(conn, compra["producto_id"])


def registrar_ajuste(conn, *, fecha, producto_id, cantidad_delta, motivo):
    prod = productos_repo.get_producto(conn, producto_id)
    if not prod:
        raise ValueError("Producto no encontrado")
    try:
        delta = int(cantidad_delta)
    except (TypeError, ValueError):
        raise ValueError("cantidad_delta debe ser un entero")
    if delta == 0:
        raise ValueError("El ajuste no puede ser cero")
    if not motivo or not motivo.strip():
        raise ValueError("El motivo es obligatorio")
    if delta < 0 and prod["stock_actual"] + delta < 0:
        raise ValueError("El ajuste dejaría stock negativo")

    creado_en = datetime.now().isoformat(timespec="seconds")
    with conn:
        inventario_repo.insert_ajuste(
            conn,
            fecha=fecha, producto_id=producto_id,
            cantidad_delta=delta, motivo=motivo.strip(), creado_en=creado_en,
        )
        _replay_cpm(conn, producto_id)


def registrar_venta_producto(conn, *, fecha, producto_id, cantidad,
                              precio_unitario):
    prod = productos_repo.get_producto(conn, producto_id)
    if not prod:
        raise ValueError("Producto no encontrado")
    if not prod["activo"]:
        raise ValueError("El producto está inactivo")
    qty = parse_positive_int(cantidad, field="cantidad")
    if qty > prod["stock_actual"]:
        raise ValueError(f"Stock insuficiente: disponible {prod['stock_actual']}")
    precio = parse_money(precio_unitario, field="precio unitario")
    if precio == 0:
        raise ValueError("El precio debe ser mayor que cero")

    cpm = Decimal(prod["costo_promedio"])
    total_venta = (precio * qty).quantize(CENT, rounding=ROUND_HALF_UP)
    costo_total = (cpm * qty).quantize(CENT, rounding=ROUND_HALF_UP)
    creado_en = datetime.now().isoformat(timespec="seconds")

    with conn:
        venta_id = ventas_producto_repo.insert_venta(
            conn,
            fecha=fecha, producto_id=producto_id, cantidad=qty,
            precio_unitario=fmt(precio), total_venta=fmt(total_venta),
            costo_unitario_snapshot=fmt(cpm),
            costo_total_snapshot=fmt(costo_total),
            creado_en=creado_en,
        )
        _replay_cpm(conn, producto_id)
    return venta_id


def anular_venta_producto(conn, *, venta_id, motivo):
    if not motivo or not motivo.strip():
        raise ValueError("El motivo es obligatorio")
    venta = ventas_producto_repo.get_venta(conn, venta_id)
    if not venta:
        raise ValueError("Venta no encontrada")
    if venta["estado"] != "valida":
        raise ValueError("La venta ya está anulada")
    with conn:
        ventas_producto_repo.marcar_venta_anulada(
            conn, venta_id, motivo.strip()
        )
        _replay_cpm(conn, venta["producto_id"])