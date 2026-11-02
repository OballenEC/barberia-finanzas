from datetime import date, timedelta

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash)

from app.data.db import get_db
from app.data.repositories import gastos_repo as repo
from app.domain import gastos as domain

bp = Blueprint("gastos", __name__, url_prefix="/gastos")


def _rango_semana():
    hoy = date.today()
    inicio = hoy - timedelta(days=hoy.weekday())
    fin = inicio + timedelta(days=7)
    return inicio.isoformat(), fin.isoformat()


@bp.route("/")
def listado():
    conn = get_db()
    inicio, fin = _rango_semana()
    gastos = repo.list_gastos_periodo(conn, inicio, fin)
    return render_template("gastos/list.html", gastos=gastos,
                           inicio=inicio, fin=fin)


@bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    conn = get_db()
    if request.method == "POST":
        try:
            domain.registrar_gasto(
                conn,
                fecha=request.form["fecha"],
                descripcion=request.form["descripcion"],
                categoria=request.form["categoria"],
                importe=request.form["importe"],
                metodo_pago=request.form["metodo_pago"],
            )
            flash("Gasto registrado", "success")
            return redirect(url_for("gastos.listado"))
        except Exception as e:
            flash(str(e), "error")
    return render_template("gastos/form.html",
                           hoy=date.today().isoformat())


@bp.route("/<int:gasto_id>/anular", methods=["POST"])
def anular(gasto_id):
    conn = get_db()
    try:
        domain.anular_gasto(
            conn, gasto_id=gasto_id, motivo=request.form.get("motivo", "")
        )
        flash("Gasto anulado", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("gastos.listado"))