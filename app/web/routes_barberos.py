from flask import Blueprint, render_template, request, redirect, url_for, flash

from app.data.db import get_db
from app.data.repositories import barberos_repo as repo
from app.domain import barberos as domain

bp = Blueprint("barberos", __name__, url_prefix="/barberos")


@bp.route("/")
def listado():
    conn = get_db()
    barberos = repo.list_barberos(conn, solo_activos=False)
    return render_template("barberos/list.html", barberos=barberos)


@bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    conn = get_db()
    if request.method == "POST":
        try:
            domain.crear_barbero(
                conn,
                nombre=request.form["nombre"],
                comision_pct_default=request.form["comision_pct_default"],
            )
            flash("Barbero creado", "success")
            return redirect(url_for("barberos.listado"))
        except Exception as e:
            flash(str(e), "error")
    return render_template("barberos/form.html")