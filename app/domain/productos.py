from .money import parse_money, fmt
from app.data.repositories import productos_repo as repo


def crear_producto(conn, *, nombre, codigo_interno, precio_venta):
    if not nombre or not nombre.strip():
        raise ValueError("El nombre es obligatorio")
    precio = parse_money(precio_venta, field="precio de venta")
    if precio == 0:
        raise ValueError("El precio de venta debe ser mayor que cero")
    codigo = (codigo_interno or "").strip() or None
    with conn:
        return repo.insert_producto(
            conn,
            nombre=nombre.strip(),
            codigo_interno=codigo,
            precio_venta=fmt(precio),
        )