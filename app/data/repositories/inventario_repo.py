def insert_compra(conn, *, fecha, producto_id, cantidad, costo_unitario,
                  total, creado_en):
    cur = conn.execute(
        "INSERT INTO compras_inventario "
        "(fecha, producto_id, cantidad, costo_unitario, total, estado, creado_en) "
        "VALUES (?, ?, ?, ?, ?, 'valida', ?)",
        (fecha, producto_id, cantidad, costo_unitario, total, creado_en),
    )
    return cur.lastrowid


def get_compra(conn, compra_id):
    return conn.execute(
        "SELECT * FROM compras_inventario WHERE id = ?", (compra_id,)
    ).fetchone()


def marcar_compra_anulada(conn, compra_id, motivo):
    conn.execute(
        "UPDATE compras_inventario "
        "SET estado = 'anulada', motivo_anulacion = ? "
        "WHERE id = ? AND estado = 'valida'",
        (motivo, compra_id),
    )


def list_compras_periodo(conn, inicio, fin):
    return conn.execute(
        "SELECT c.*, p.nombre AS producto_nombre "
        "FROM compras_inventario c JOIN productos p ON p.id = c.producto_id "
        "WHERE c.fecha >= ? AND c.fecha < ? "
        "ORDER BY c.fecha DESC, c.id DESC",
        (inicio, fin),
    ).fetchall()


def insert_ajuste(conn, *, fecha, producto_id, cantidad_delta, motivo,
                  creado_en):
    cur = conn.execute(
        "INSERT INTO ajustes_inventario "
        "(fecha, producto_id, cantidad_delta, motivo, creado_en) "
        "VALUES (?, ?, ?, ?, ?)",
        (fecha, producto_id, cantidad_delta, motivo, creado_en),
    )
    return cur.lastrowid


def list_ajustes(conn, producto_id=None):
    q = ("SELECT a.*, p.nombre AS producto_nombre "
         "FROM ajustes_inventario a JOIN productos p ON p.id = a.producto_id")
    args = ()
    if producto_id:
        q += " WHERE a.producto_id = ?"
        args = (producto_id,)
    q += " ORDER BY a.fecha DESC, a.id DESC"
    return conn.execute(q, args).fetchall()