def insert_producto(conn, *, nombre, codigo_interno, precio_venta):
    cur = conn.execute(
        "INSERT INTO productos (nombre, codigo_interno, costo_promedio, precio_venta, stock_actual, activo) "
        "VALUES (?, ?, '0.00', ?, 0, 1)",
        (nombre, codigo_interno, precio_venta),
    )
    return cur.lastrowid


def get_producto(conn, producto_id):
    return conn.execute(
        "SELECT * FROM productos WHERE id = ?", (producto_id,)
    ).fetchone()


def list_productos(conn, solo_activos=True):
    q = "SELECT * FROM productos"
    if solo_activos:
        q += " WHERE activo = 1"
    q += " ORDER BY nombre"
    return conn.execute(q).fetchall()


def desactivar_producto(conn, producto_id):
    conn.execute("UPDATE productos SET activo = 0 WHERE id = ?", (producto_id,))