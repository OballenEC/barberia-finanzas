from flask import Blueprint, render_template, request, redirect, url_for, flash

from app.data.db import get_db
from app.data.repositories import productos_repo as repo
from app.domain import productos as domain

bp = Blueprint("productos", __name__, url_prefix="/productos")


@bp.route("/")
def listado():
    conn = get_db()
    productos = repo.list_productos(conn, solo_activos=False)
    return render_template("productos/list.html", productos=productos)


@bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    conn = get_db()
    if request.method == "POST":
        try:
            domain.crear_producto(
                conn,
                nombre=request.form["nombre"],
                codigo_interno=request.form.get("codigo_interno", ""),
                precio_venta=request.form["precio_venta"],
            )
            flash("Producto creado", "success")
            return redirect(url_for("productos.listado"))
        except Exception as e:
            flash(str(e), "error")
    return render_template("productos/form.html")