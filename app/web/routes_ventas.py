from datetime import date, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash

from app.data.db import get_db
from app.data.repositories import productos_repo, ventas_producto_repo as repo
from app.domain import inventario as domain

bp = Blueprint("ventas", __name__, url_prefix="/ventas")


def _rango_semana():
    hoy = date.today()
    inicio = hoy - timedelta(days=hoy.weekday())
    fin = inicio + timedelta(days=7)
    return inicio.isoformat(), fin.isoformat()


@bp.route("/")
def listado():
    conn = get_db()
    inicio, fin = _rango_semana()
    ventas = repo.list_ventas_periodo(conn, inicio, fin)
    return render_template(
        "ventas/list.html", ventas=ventas, inicio=inicio, fin=fin,
    )


@bp.route("/nueva", methods=["GET", "POST"])
def nueva():
    conn = get_db()
    productos = productos_repo.list_productos(conn)
    if request.method == "POST":
        try:
            domain.registrar_venta_producto(
                conn,
                fecha=request.form["fecha"],
                producto_id=int(request.form["producto_id"]),
                cantidad=request.form["cantidad"],
                precio_unitario=request.form["precio_unitario"],
            )
            flash("Venta registrada", "success")
            return redirect(url_for("ventas.listado"))
        except Exception as e:
            flash(str(e), "error")
    return render_template(
        "ventas/form.html",
        productos=productos, hoy=date.today().isoformat(),
    )


@bp.route("/<int:venta_id>/anular", methods=["POST"])
def anular(venta_id):
    conn = get_db()
    try:
        domain.anular_venta_producto(
            conn, venta_id=venta_id,
            motivo=request.form.get("motivo", ""),
        )
        flash("Venta anulada", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("ventas.listado"))