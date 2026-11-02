def insert_barbero(conn, *, nombre, comision_pct_default):
    cur = conn.execute(
        "INSERT INTO barberos (nombre, comision_pct_default, activo) "
        "VALUES (?, ?, 1)",
        (nombre, comision_pct_default),
    )
    return cur.lastrowid


def get_barbero(conn, barbero_id):
    return conn.execute(
        "SELECT * FROM barberos WHERE id = ?", (barbero_id,)
    ).fetchone()


def list_barberos(conn, solo_activos=True):
    q = "SELECT * FROM barberos"
    if solo_activos:
        q += " WHERE activo = 1"
    q += " ORDER BY nombre"
    return conn.execute(q).fetchall()


def desactivar_barbero(conn, barbero_id):
    conn.execute("UPDATE barberos SET activo = 0 WHERE id = ?", (barbero_id,))