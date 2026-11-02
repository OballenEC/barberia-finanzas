from datetime import date, datetime, timedelta

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash)

from app.data.db import get_db
from app.data.repositories import servicios_repo as repo
from app.domain import servicios as domain

bp = Blueprint("servicios", __name__, url_prefix="/servicios")


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
    return render_template("servicios/list.html", ventas=ventas,
                           inicio=inicio, fin=fin)


@bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    conn = get_db()
    servicios = repo.list_servicios_activos(conn)
    if request.method == "POST":
        try:
            fecha_local = request.form["fecha_hora"]  # yyyy-mm-ddTHH:MM
            fecha_iso = datetime.fromisoformat(fecha_local).isoformat(
                timespec="seconds"
            )
            domain.registrar_venta_servicio(
                conn,
                servicio_id=int(request.form["servicio_id"]),
                fecha_hora=fecha_iso,
                precio_cobrado=request.form["precio_cobrado"],
                metodo_pago=request.form["metodo_pago"],
            )
            flash("Servicio registrado", "success")
            return redirect(url_for("servicios.listado"))
        except Exception as e:
            flash(str(e), "error")
    return render_template("servicios/form.html", servicios=servicios,
                           ahora=datetime.now().strftime("%Y-%m-%dT%H:%M"))


@bp.route("/<int:venta_id>/anular", methods=["POST"])
def anular(venta_id):
    conn = get_db()
    try:
        domain.anular_venta_servicio(
            conn, venta_id=venta_id, motivo=request.form.get("motivo", "")
        )
        flash("Venta anulada", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("servicios.listado"))