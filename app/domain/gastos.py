from datetime import datetime

from .money import parse_money, fmt
from app.data.repositories import gastos_repo as repo

VALID_METODOS = {"efectivo", "tarjeta", "transferencia", "otro"}


def registrar_gasto(conn, *, fecha, descripcion, categoria, importe,
                    metodo_pago):
    if not descripcion or not descripcion.strip():
        raise ValueError("La descripción es obligatoria")
    if not categoria or not categoria.strip():
        raise ValueError("La categoría es obligatoria")
    if metodo_pago not in VALID_METODOS:
        raise ValueError(f"Método de pago inválido: {metodo_pago}")

    imp = parse_money(importe, field="importe")
    if imp == 0:
        raise ValueError("El importe debe ser mayor que cero")

    creado_en = datetime.now().isoformat(timespec="seconds")
    with conn:
        return repo.insert_gasto(
            conn,
            fecha=fecha,
            descripcion=descripcion.strip(),
            categoria=categoria.strip(),
            importe=fmt(imp),
            metodo_pago=metodo_pago,
            creado_en=creado_en,
        )


def anular_gasto(conn, *, gasto_id, motivo):
    if not motivo or not motivo.strip():
        raise ValueError("El motivo de anulación es obligatorio")
    gasto = repo.get_gasto(conn, gasto_id)
    if not gasto:
        raise ValueError("Gasto no encontrado")
    if gasto["estado"] != "valida":
        raise ValueError("El gasto ya está anulado")
    with conn:
        repo.marcar_gasto_anulado(conn, gasto_id, motivo.strip())