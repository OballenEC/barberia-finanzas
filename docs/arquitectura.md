# Arquitectura

## 1. Visión general

Aplicación web monolítica con arquitectura por capas. El objetivo es separar responsabilidades para que las reglas de negocio puedan probarse sin Flask ni SQLite, y para que los reportes sean independientes del acceso a datos.

## 2. Capas

    +--------------------------------------------+
    |  web/ (rutas Flask + render Jinja2)        |
    |  - routes_servicios.py                     |
    |  - routes_barberos.py                      |
    |  - routes_gastos.py                        |
    |  - routes_productos.py                     |
    |  - routes_inventario.py                    |
    |  - routes_ventas.py                        |
    |  - routes_reportes.py                      |
    |  - routes_panel.py                         |
    +------------------+-------------------------+
                       |
    +------------------v-------------------------+
    |  domain/ (reglas de negocio, sin Flask)    |
    |  - servicios.py     - inventario.py        |
    |  - gastos.py        - productos.py         |
    |  - barberos.py      - money.py             |
    +------------------+-------------------------+
                       |
    +------------------v-------------------------+
    |  reports/ (cálculos financieros, solo lee) |
    |  - panel.py    - diario.py                 |
    |  - semanal.py  - barbero.py                |
    |  - _rango.py                               |
    +------------------+-------------------------+
                       |
    +------------------v-------------------------+
    |  data/ (SQLite + repositorios)             |
    |  - db.py       - schema.sql                |
    |  - seed_demo.sql                           |
    |  - repositories/*.py                       |
    +--------------------------------------------+

## 3. Responsabilidades por capa

### web/
- Recibe requests HTTP y formula respuestas.
- Valida parámetros de formularios de forma superficial (campos obligatorios).
- Delega a domain/ o reports/ según corresponda.
- Renderiza templates Jinja2.
- Nunca ejecuta SQL directamente.

### domain/
- Contiene las reglas de negocio.
- No importa Flask ni Jinja2.
- Sí puede importar data/ (repositorios) para persistencia.
- Usa Decimal para todo importe monetario (nunca float).
- Valida: precios >= 0, cantidades > 0, stock suficiente, motivos de anulación, porcentajes de comisión entre 0 y 100.
- Congela snapshots al momento de registrar: costo unitario en ventas de producto, % de comisión en servicios y ventas.

### reports/
- Solo lectura. No escribe en base de datos.
- Recibe conn (conexión SQLite) y rangos de fecha normalizados.
- Calcula KPIs financieros aplicando reglas anti-doble-conteo.
- Devuelve diccionarios con Decimal para los templates.

### data/
- Único punto de contacto con SQLite.
- db.py gestiona la conexión por request.
- schema.sql es la fuente de verdad del DDL.
- seed_demo.sql y scripts/seed_demo.py cargan datos de demostración idempotentes.
- repositories/ agrupa consultas por entidad. Las queries usan siempre parámetros (?) para prevenir inyección SQL.

## 4. Decisiones técnicas clave

| # | Decisión | Justificación |
|---|---|---|
| D1 | Decimal-as-TEXT en SQLite | Evita errores de flotantes en cálculos financieros. SQLite no tiene tipo decimal nativo. |
| D2 | CPM con snapshot por venta | COGS histórico inmutable. El reporte de una venta pasada no cambia si el costo sube después. |
| D3 | Snapshot del % de comisión por venta | Cambiar el % de un barbero no altera comisiones históricas. |
| D4 | Anulaciones auditables, no borrado | Nada se pierde. Toda operación anulada queda en historial y se excluye de totales. |
| D5 | Bloqueo de anulación de compra con ventas posteriores | Evita corromper el COGS histórico. Se sugiere usar ajuste de inventario. |
| D6 | Comisiones como línea separada del resultado | El cliente pidió distinguirlas. No se descuentan del ingreso bruto. |
| D7 | Compras de inventario fuera del resultado | Solo COGS resta. Regla contable estándar. Compras se muestran como flujo informativo. |
| D8 | _rango.py con rango_exclusivo() | Normaliza fechas DATE y DATETIME para reportes que consultan tablas mixtas. |
| D9 | Flask + Jinja2 sin SPA | MVP simple, mobile-first, sin dependencia de Node/npm. |
| D10 | SQLite en archivo, no en memoria | Persistencia real entre reinicios. Pruebas usan archivo temporal. |

## 5. Flujo de un request (ejemplo: registrar un servicio)

1. Usuario envía formulario POST a /servicios/nuevo.
2. routes_servicios.py recibe los campos: servicio_id, barbero_id, fecha_hora, precio_cobrado, metodo_pago, comision_pct_override (opcional).
3. domain/servicios.py::registrar_venta_servicio():
   - Valida que el servicio exista y esté activo.
   - Valida el método de pago.
   - Parsea precio_cobrado a Decimal.
   - Si hay barbero_id, delega a domain/barberos.py::resolver_pct() para obtener el % efectivo.
   - Calcula comision_monto = precio * pct / 100 redondeando a 2 decimales (HALF_UP).
   - Persiste vía repositories/servicios_repo.py con INSERT parametrizado.
4. La transacción se cierra con with conn: (commit atómico).
5. routes_servicios.py redirige a /servicios/ con mensaje flash.
6. La lista se renderiza consultando list_ventas_periodo(), que JOINea con servicios y barberos para mostrar nombres.

## 6. Flujo de una venta de producto (ejemplo: 2 ceras vendidas)

1. routes_ventas.py recibe POST en /ventas/nueva.
2. domain/inventario.py::registrar_venta_producto():
   - Valida que el producto exista y esté activo.
   - Valida cantidad > 0 y stock suficiente.
   - Lee costo_promedio actual del producto (CPM).
   - Congela: costo_unitario_snapshot = cpm, costo_total_snapshot = cpm * cantidad.
   - Inserta la venta con snapshots.
   - Llama a _replay_cpm() para recalcular stock_actual y costo_promedio desde las tablas origen.
3. _replay_cpm():
   - Lee todos los eventos (compras_inventario, ventas_producto, ajustes_inventario) del producto.
   - Los ordena cronológicamente.
   - Recalcula stock y CPM aplicando compras y ventas en orden.
   - Actualiza productos.stock_actual y productos.costo_promedio.

## 7. Convenciones del proyecto

- Importes monetarios: siempre Decimal con 2 decimales, ROUND_HALF_UP. Nunca float.
- Fechas: YYYY-MM-DD para columnas DATE, YYYY-MM-DDTHH:MM:SS para columnas DATETIME (ISO-8601, hora local).
- IDs: AUTOINCREMENT en SQLite, nunca asignados manualmente.
- Estados: valida o anulada. Nunca borrada.
- Anulaciones: siempre con motivo_anulacion no vacío.
- Seed keys: string estable en datos demo, NULL en datos reales.
- Commits: uno por hito verificado, con mensaje en español.

## 8. Testing

- tests/conftest.py provee fixtures conn (BD con catálogos) y conn_vacia (solo schema).
- Cada test corre en su propia BD SQLite temporal. Aislados entre sí.
- Los tests no levantan Flask; prueban dominio y reportes directamente.
- La suite completa toma ~3 segundos.

## 9. Riesgos conocidos y mitigaciones

| Riesgo | Mitigación implementada |
|---|---|
| Error de redondeo en dinero | Decimal + ROUND_HALF_UP en todos los cálculos |
| COGS histórico incorrecto | Snapshot congelado en cada venta |
| Comisiones históricas alteradas | Snapshot de % por venta |
| Operaciones borradas por accidente | Anulación auditable con motivo; nunca DELETE |
| Inconsistencia de stock | _replay_cpm() recalcula desde eventos válidos |
| Rango de fecha mal calculado | _rango.rango_exclusivo() normaliza DATE y DATETIME |
| Inyección SQL | Queries parametrizadas con ? en todos los repositorios |

## 10. Extensiones futuras

- Autenticación con Flask-Login.
- Bootstrap 5 o template admin para UI.
- Smoke y Ping Pong como entidades propias (pendiente de aclaración).
- Reportes exportables a PDF/CSV.
- Respaldos automáticos programados.
- Multi-sucursal (requiere añadir sucursal_id a todas las tablas).