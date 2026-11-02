from datetime import date, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash

from app.data.db import get_db
from app.data.repositories import productos_repo, inventario_repo as repo
from app.domain import inventario as domain

bp = Blueprint("inventario", __name__, url_prefix="/inventario")


def _rango_semana():
    hoy = date.today()
    inicio = hoy - timedelta(days=hoy.weekday())
    fin = inicio + timedelta(days=7)
    return inicio.isoformat(), fin.isoformat()


@bp.route("/")
def listado():
    conn = get_db()
    inicio, fin = _rango_semana()
    compras = repo.list_compras_periodo(conn, inicio, fin)
    ajustes = repo.list_ajustes(conn)
    productos = productos_repo.list_productos(conn, solo_activos=False)
    return render_template(
        "inventario/list.html",
        compras=compras, ajustes=ajustes, productos=productos,
        inicio=inicio, fin=fin,
    )


@bp.route("/compra/nueva", methods=["GET", "POST"])
def nueva_compra():
    conn = get_db()
    productos = productos_repo.list_productos(conn)
    if request.method == "POST":
        try:
            domain.registrar_compra(
                conn,
                fecha=request.form["fecha"],
                producto_id=int(request.form["producto_id"]),
                cantidad=request.form["cantidad"],
                costo_unitario=request.form["costo_unitario"],
            )
            flash("Compra registrada", "success")
            return redirect(url_for("inventario.listado"))
        except Exception as e:
            flash(str(e), "error")
    return render_template(
        "inventario/compra_form.html",
        productos=productos, hoy=date.today().isoformat(),
    )


@bp.route("/compra/<int:compra_id>/anular", methods=["POST"])
def anular_compra(compra_id):
    conn = get_db()
    try:
        domain.anular_compra(
            conn, compra_id=compra_id,
            motivo=request.form.get("motivo", ""),
        )
        flash("Compra anulada", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("inventario.listado"))


@bp.route("/ajuste/nuevo", methods=["GET", "POST"])
def nuevo_ajuste():
    conn = get_db()
    productos = productos_repo.list_productos(conn, solo_activos=False)
    if request.method == "POST":
        try:
            domain.registrar_ajuste(
                conn,
                fecha=request.form["fecha"],
                producto_id=int(request.form["producto_id"]),
                cantidad_delta=request.form["cantidad_delta"],
                motivo=request.form["motivo"],
            )
            flash("Ajuste registrado", "success")
            return redirect(url_for("inventario.listado"))
        except Exception as e:
            flash(str(e), "error")
    return render_template(
        "inventario/ajuste_form.html",
        productos=productos, hoy=date.today().isoformat(),
    )