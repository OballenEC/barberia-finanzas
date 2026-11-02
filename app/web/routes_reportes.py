from datetime import date

from flask import Blueprint, render_template, request

from app.data.db import get_db
from app.data.repositories import barberos_repo
from app.reports.diario import calcular_diario
from app.reports.semanal import calcular_semanal, rango_semana
from app.reports.barbero import calcular_reporte_barbero

bp = Blueprint("reportes", __name__, url_prefix="/reportes")


@bp.route("/diario")
def diario():
    conn = get_db()
    fecha = request.args.get("fecha") or date.today().isoformat()
    data = calcular_diario(conn, fecha)
    return render_template("reportes/diario.html", data=data)


@bp.route("/semanal")
def semanal():
    conn = get_db()
    fecha_ref = request.args.get("semana")
    data = calcular_semanal(conn, fecha_ref)
    return render_template("reportes/semanal.html", data=data)


@bp.route("/barbero")
def barbero():
    conn = get_db()
    fecha_ref = request.args.get("semana")
    barbero_id_raw = request.args.get("barbero_id", "").strip()
    barbero_id = int(barbero_id_raw) if barbero_id_raw else None

    lunes, domingo = rango_semana(fecha_ref)
    inicio_iso = f"{lunes}T00:00:00"
    fin_iso = f"{domingo}T23:59:59"

    filas = calcular_reporte_barbero(conn, inicio_iso, fin_iso, barbero_id)
    barberos = barberos_repo.list_barberos(conn, solo_activos=False)

    return render_template(
        "reportes/barbero.html",
        filas=filas,
        barberos=barberos,
        barbero_id_sel=barbero_id,
        lunes=lunes,
        domingo=domingo,
    )