def get_servicio(conn, servicio_id):
    return conn.execute(
        "SELECT * FROM servicios WHERE id = ?", (servicio_id,)
    ).fetchone()


def list_servicios_activos(conn):
    return conn.execute(
        "SELECT * FROM servicios WHERE activo = 1 ORDER BY nombre"
    ).fetchall()


def insert_venta_servicio(conn, *, servicio_id, barbero_id, fecha_hora,
                          precio_cobrado, metodo_pago, comision_pct,
                          comision_monto, creado_en):
    cur = conn.execute(
        """INSERT INTO ventas_servicio
           (servicio_id, barbero_id, fecha_hora, precio_cobrado, metodo_pago,
            comision_pct, comision_monto, estado, creado_en)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'valida', ?)""",
        (servicio_id, barbero_id, fecha_hora, precio_cobrado, metodo_pago,
         comision_pct, comision_monto, creado_en),
    )
    return cur.lastrowid


def get_venta_servicio(conn, venta_id):
    return conn.execute(
        "SELECT * FROM ventas_servicio WHERE id = ?", (venta_id,)
    ).fetchone()


def marcar_venta_servicio_anulada(conn, venta_id, motivo):
    conn.execute(
        """UPDATE ventas_servicio
           SET estado = 'anulada', motivo_anulacion = ?
           WHERE id = ? AND estado = 'valida'""",
        (motivo, venta_id),
    )


def list_ventas_periodo(conn, inicio_iso, fin_iso):
    return conn.execute(
        """SELECT vs.*, s.nombre AS servicio_nombre,
                  b.nombre AS barbero_nombre
           FROM ventas_servicio vs
           JOIN servicios s ON s.id = vs.servicio_id
           LEFT JOIN barberos b ON b.id = vs.barbero_id
           WHERE vs.fecha_hora >= ? AND vs.fecha_hora < ?
           ORDER BY vs.fecha_hora DESC, vs.id DESC""",
        (inicio_iso, fin_iso),
    ).fetchall()