from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from .money import parse_money, fmt
from . import barberos as dom_barberos
from app.data.repositories import servicios_repo as repo

CENT = Decimal("0.01")
VALID_METODOS = {"efectivo", "tarjeta", "transferencia", "otro"}


def registrar_venta_servicio(conn, *, servicio_id, fecha_hora,
                             precio_cobrado, metodo_pago,
                             barbero_id=None, comision_pct_override=None):
    servicio = repo.get_servicio(conn, servicio_id)
    if not servicio:
        raise ValueError("Servicio no encontrado")
    if not servicio["activo"]:
        raise ValueError("El servicio está inactivo")
    if metodo_pago not in VALID_METODOS:
        raise ValueError(f"Método de pago inválido: {metodo_pago}")

    precio = parse_money(precio_cobrado, field="precio cobrado")

    comision_pct = None
    comision_monto = None
    if barbero_id is not None:
        pct = dom_barberos.resolver_pct(conn, barbero_id, comision_pct_override)
        comision_pct = fmt(pct)
        comision_monto = fmt(
            (precio * pct / Decimal("100")).quantize(CENT, rounding=ROUND_HALF_UP)
        )

    creado_en = datetime.now().isoformat(timespec="seconds")

    with conn:
        return repo.insert_venta_servicio(
            conn,
            servicio_id=servicio_id,
            barbero_id=barbero_id,
            fecha_hora=fecha_hora,
            precio_cobrado=fmt(precio),
            metodo_pago=metodo_pago,
            comision_pct=comision_pct,
            comision_monto=comision_monto,
            creado_en=creado_en,
        )


def anular_venta_servicio(conn, *, venta_id, motivo):
    if not motivo or not motivo.strip():
        raise ValueError("El motivo de anulación es obligatorio")
    venta = repo.get_venta_servicio(conn, venta_id)
    if not venta:
        raise ValueError("Venta no encontrada")
    if venta["estado"] != "valida":
        raise ValueError("La venta ya está anulada")
    with conn:
        repo.marcar_venta_servicio_anulada(conn, venta_id, motivo.strip())