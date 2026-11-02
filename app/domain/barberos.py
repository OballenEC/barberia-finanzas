from decimal import Decimal

from .money import parse_money, fmt
from app.data.repositories import barberos_repo as repo


def _parse_pct(value, field="comisión %"):
    pct = parse_money(value, field=field)
    if pct < 0 or pct > 100:
        raise ValueError(f"{field} debe estar entre 0 y 100")
    return pct


def crear_barbero(conn, *, nombre, comision_pct_default):
    if not nombre or not nombre.strip():
        raise ValueError("El nombre del barbero es obligatorio")
    pct = _parse_pct(comision_pct_default)
    with conn:
        return repo.insert_barbero(
            conn,
            nombre=nombre.strip(),
            comision_pct_default=fmt(pct),
        )


def obtener_o_error(conn, barbero_id):
    b = repo.get_barbero(conn, barbero_id)
    if not b:
        raise ValueError("Barbero no encontrado")
    if not b["activo"]:
        raise ValueError("El barbero está inactivo")
    return b


def resolver_pct(conn, barbero_id, override_pct=None):
    """Devuelve el % a aplicar (override si viene, si no default del barbero)."""
    barbero = obtener_o_error(conn, barbero_id)
    if override_pct is not None and str(override_pct).strip() != "":
        return _parse_pct(override_pct)
    return Decimal(barbero["comision_pct_default"])