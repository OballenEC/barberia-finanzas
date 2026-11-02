from flask import Blueprint, render_template, request, current_app

from app.data.db import get_db
from app.reports.panel import calcular_panel
from app.reports.semanal import rango_semana

bp = Blueprint("panel", __name__)


@bp.route("/")
def index():
    conn = get_db()
    fecha_ref = request.args.get("semana")
    lunes, domingo = rango_semana(fecha_ref)
    inicio_iso = f"{lunes}T00:00:00"
    fin_iso = f"{domingo}T23:59:59"

    kpis = calcular_panel(conn, inicio_iso, fin_iso)

    return render_template(
        "panel/index.html",
        demo_mode=current_app.config["DEMO_MODE"],
        lunes=lunes,
        domingo=domingo,
        kpis=kpis,
    )