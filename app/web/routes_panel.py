from flask import Blueprint, render_template, current_app

bp = Blueprint("panel", __name__)

@bp.route("/")
def index():
    return render_template("panel/index.html", demo_mode=current_app.config["DEMO_MODE"])