def insert_venta(conn, *, fecha, producto_id, cantidad, precio_unitario,
                 total_venta, costo_unitario_snapshot, costo_total_snapshot,
                 creado_en):
    cur = conn.execute(
        "INSERT INTO ventas_producto "
        "(fecha, producto_id, cantidad, precio_unitario, total_venta, "
        " costo_unitario_snapshot, costo_total_snapshot, estado, creado_en) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, 'valida', ?)",
        (fecha, producto_id, cantidad, precio_unitario, total_venta,
         costo_unitario_snapshot, costo_total_snapshot, creado_en),
    )
    return cur.lastrowid


def get_venta(conn, venta_id):
    return conn.execute(
        "SELECT * FROM ventas_producto WHERE id = ?", (venta_id,)
    ).fetchone()


def marcar_venta_anulada(conn, venta_id, motivo):
    conn.execute(
        "UPDATE ventas_producto "
        "SET estado = 'anulada', motivo_anulacion = ? "
        "WHERE id = ? AND estado = 'valida'",
        (motivo, venta_id),
    )


def list_ventas_periodo(conn, inicio, fin):
    return conn.execute(
        "SELECT v.*, p.nombre AS producto_nombre "
        "FROM ventas_producto v JOIN productos p ON p.id = v.producto_id "
        "WHERE v.fecha >= ? AND v.fecha < ? "
        "ORDER BY v.fecha DESC, v.id DESC",
        (inicio, fin),
    ).fetchall()