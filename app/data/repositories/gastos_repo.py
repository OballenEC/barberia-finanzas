def insert_gasto(conn, *, fecha, descripcion, categoria, importe,
                 metodo_pago, creado_en):
    cur = conn.execute(
        """INSERT INTO gastos_operativos
           (fecha, descripcion, categoria, importe, metodo_pago,
            estado, creado_en)
           VALUES (?, ?, ?, ?, ?, 'valida', ?)""",
        (fecha, descripcion, categoria, importe, metodo_pago, creado_en),
    )
    return cur.lastrowid


def get_gasto(conn, gasto_id):
    return conn.execute(
        "SELECT * FROM gastos_operativos WHERE id = ?", (gasto_id,)
    ).fetchone()


def marcar_gasto_anulado(conn, gasto_id, motivo):
    conn.execute(
        """UPDATE gastos_operativos
           SET estado = 'anulada', motivo_anulacion = ?
           WHERE id = ? AND estado = 'valida'""",
        (motivo, gasto_id),
    )


def list_gastos_periodo(conn, inicio_iso, fin_iso):
    return conn.execute(
        """SELECT * FROM gastos_operativos
           WHERE fecha >= ? AND fecha < ?
           ORDER BY fecha DESC, id DESC""",
        (inicio_iso, fin_iso),
    ).fetchall()