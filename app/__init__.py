from flask import Flask
from .config import get_config
from .data import db as db_module


def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(get_config(config_name))

    db_module.init_app(app)

    from .web import routes_panel
    app.register_blueprint(routes_panel.bp)

    from .web import routes_barberos
    app.register_blueprint(routes_barberos.bp)

    from .web import routes_servicios
    app.register_blueprint(routes_servicios.bp)

    from .web import routes_gastos
    app.register_blueprint(routes_gastos.bp)

    from .web import routes_productos
    app.register_blueprint(routes_productos.bp)

    from .web import routes_inventario
    app.register_blueprint(routes_inventario.bp)

    from .web import routes_ventas
    app.register_blueprint(routes_ventas.bp)

    return app