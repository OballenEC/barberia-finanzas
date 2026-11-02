# Flujo de operaciones y decisiones

Documento textual que describe cmo se registran las operaciones y cmo fluyen los datos. Base para diagramas visuales en Canva.

## 1. Flujo: registrar un servicio (corte)

    [Usuario]
       |
       v
    /servicios/nuevo (GET)
       |
       v
    Formulario: servicio, barbero (opcional), fecha_hora, precio_cobrado, metodo_pago, comision_pct_override (opcional)
       |
       v (POST)
    routes_servicios.nuevo
       |
       v
    domain.servicios.registrar_venta_servicio()
       |
       +--> Valida: servicio existe y activo
       +--> Valida: metodo_pago valido
       +--> Parsea precio_cobrado -> Decimal
       |
       +--> Si barbero_id presente:
       |      |
       |      v
       |    domain.barberos.resolver_pct(barbero_id, override)
       |      |
       |      +--> Si hay override: usa override
       |      +--> Si no: usa comision_pct_default del barbero
       |      |
       |      v
       |    Calcula comision_monto = precio * pct / 100 (HALF_UP, 2 dec)
       |
       v
    services_repo.insert_venta_servicio() -- INSERT con snapshots
       |
       v
    COMMIT
       |
       v
    Redirect a /servicios/ con flash "Servicio registrado"

**Snapshot crtico:** comision_pct y comision_monto se congelan en la fila. Cambiar el % del barbero después no modifica ventas pasadas.

## 2. Flujo: anular un servicio

    [Usuario] -> form con motivo -> POST /servicios/<id>/anular
       |
       v
    domain.servicios.anular_venta_servicio()
       |
       +--> Valida motivo no vaco
       +--> Consulta venta por id
       +--> Valida estado == 'valida' (si ya anulada, error)
       |
       v
    UPDATE ventas_servicio SET estado='anulada', motivo_anulacion=?
       |
       v
    COMMIT

**Efecto:** la venta sigue en historial con estado='anulada'. No suma a reportes. Se puede ver el motivo.

## 3. Flujo: registrar una compra de inventario

    [Usuario] -> /inventario/compra/nueva
       |
       v
    Formulario: fecha, producto, cantidad, costo_unitario
       |
       v (POST)
    domain.inventario.registrar_compra()
       |
       +--> Valida producto existe y activo
       +--> Valida cantidad > 0 y costo_unitario > 0
       +--> Calcula total = cantidad * costo_unitario
       |
       v
    INSERT compras_inventario (estado='valida')
       |
       v
    _replay_cpm(producto_id)
       |
       +--> Lee TODAS las compras validadas del producto
       +--> Lee TODAS las ventas validadas del producto
       +--> Lee TODOS los ajustes del producto
       +--> Ordena eventos cronologicamente
       +--> Recalcula stock y CPM desde cero
       +--> UPDATE productos SET stock_actual=?, costo_promedio=?
       |
       v
    COMMIT

**Por qu replay y no incremental:** al anular compras o ventas, el CPM cambia retroactivamente. Recalcular desde cero es la única forma confiable de mantener consistencia.

## 4. Flujo: registrar una venta de producto

    [Usuario] -> /ventas/nueva
       |
       v (POST)
    domain.inventario.registrar_venta_producto()
       |
       +--> Valida producto existe y activo
       +--> Valida cantidad > 0
       +--> Valida stock_actual >= cantidad (si no, error "Stock insuficiente")
       +--> Parsea precio_unitario -> Decimal
       +--> Lee cpm actual del producto
       |
       +--> Calcula:
       |      total_venta = precio * cantidad
       |      costo_unitario_snapshot = cpm
       |      costo_total_snapshot = cpm * cantidad
       |      comision_monto = total_venta * pct / 100 (si barbero)
       |
       v
    INSERT ventas_producto (estado='valida') con snapshots
       |
       v
    _replay_cpm(producto_id)
       |
       v
    COMMIT

**Punto clave:** si manana el costo de reposicion sube de $80 a $100, la venta de hoy sigue con costo_unitario_snapshot = $80. El COGS historico es inmutable.

## 5. Flujo: anular una compra (regla de bloqueo)

    [Usuario] -> POST /inventario/compra/<id>/anular con motivo
       |
       v
    domain.inventario.anular_compra()
       |
       +--> Valida motivo no vaco
       +--> Consulta compra por id
       +--> Valida estado == 'valida'
       |
       +--> Verifica: COUNT(ventas_producto WHERE producto_id=?
       |                AND estado='valida'
       |                AND fecha > compra.fecha)
       |
       +--> Si COUNT > 0:
       |      |
       |      v
       |    Error: "No se puede anular: existen ventas posteriores.
       |            Usa un ajuste de inventario para corregir el stock."
       |
       +--> Si COUNT == 0:
              |
              v
           UPDATE compras_inventario SET estado='anulada'
              |
              v
           _replay_cpm(producto_id)
              |
              v
           COMMIT

**Razon del bloqueo:** si la compra "nunca ocurrio", el CPM del día de la venta fue distinto. Los snapshots de esas ventas quedarian inconsistentes. Mejor bloquear y sugerir ajuste manual.

## 6. Flujo: ajuste manual de inventario

    [Usuario] -> /inventario/ajuste/nuevo
       |
       v
    Formulario: fecha, producto, cantidad_delta (ej. -1, +3), motivo
       |
       v (POST)
    domain.inventario.registrar_ajuste()
       |
       +--> Valida producto existe
       +--> Valida cantidad_delta != 0
       +--> Valida motivo no vaco
       +--> Si delta < 0: valida stock_actual + delta >= 0
       |
       v
    INSERT ajustes_inventario
       |
       v
    _replay_cpm(producto_id)
       |
       v
    COMMIT

**Uso típico:** merma, producto daado, correccion por conteo fisico, o compensar una compra que no se puede anular.

## 7. Flujo: consultar el panel (KPIs)

    [Usuario] -> GET / (con ?semana=YYYY-MM-DD opcional)
       |
       v
    routes_panel.index
       |
       +--> Calcula rango lunes-domingo de la semana
       +--> Normaliza limites con _rango.rango_exclusivo()
       |
       v
    reports.panel.calcular_panel(conn, inicio, fin)
       |
       +--> _sum_svc: ingresos + comisiones de ventas_servicio validas
       +--> _sum_prod: ventas + COGS + comisiones de ventas_producto validas
       +--> _sum_gastos: total gastos_operativos validos
       +--> _sum_compras: total compras_inventario validas
       |
       +--> Calcula:
              margen_bruto = ventas - COGS
              resultado_neto = ingresos + ventas - COGS - gastos - comisiones_svc - comisiones_prod
              flujo_efectivo = ingresos + ventas - gastos - compras - comisiones_svc - comisiones_prod
       |
       v
    Renderiza panel/index.html con KPIs

**Regla anti-doble-conteo aplicada aquí:**
- compras_inventario NO aparece en resultado_neto.
- Solo aparece en flujo_efectivo (porque si salio dinero).
- Esta es la diferencia clave: una compra afecta el flujo pero NO el resultado operativo hasta que la unidad se vende (via COGS).

## 8. Flujo: reporte semanal con comparacion

    [Usuario] -> GET /reportes/semanal?semana=YYYY-MM-DD
       |
       v
    reports.semanal.calcular_semanal(conn, fecha_ref)
       |
       +--> rango_semana(fecha_ref) -> (lunes, domingo)
       +--> rango_semana_anterior -> (lunes-7d, domingo-7d)
       |
       +--> calcular_panel(actual) -> kpis_actual
       +--> calcular_panel(anterior) -> kpis_anterior
       |
       +--> Consulta por barbero:
              SELECT barberos + SUM(ingresos) + SUM(comisiones)
              FROM ventas_servicio WHERE rango
              GROUP BY barbero
       |
       +--> Por cada barbero, agrega ventas_producto del mismo periodo
       |
       v
    Renderiza semanal.html con dos columnas (actual vs anterior) + tabla por barbero

## 9. Flujo: reporte por barbero individual

    [Usuario] -> GET /reportes/barbero?semana=...&barbero_id=opcional
       |
       v
    reports.barbero.calcular_reporte_barbero(conn, inicio, fin, barbero_id)
       |
       +--> Lista barberos (todos activos, o el específico si se paso barbero_id)
       |
       +--> Por cada barbero:
              - Detalle de servicios (JOIN servicios)
              - Detalle de ventas producto (JOIN productos)
              - Suma ingresos, comisiones de ambos
       |
       v
    Renderiza barbero.html con tarjeta por barbero (resumen + detalles)

## 10. Diagrama de estados de una operación

    [creada]
       |
       | registrar()
       v
    [valida] ---- anular() ----> [anulada]
                                     |
                                     | (permanece en historial,
                                     |  excluida de totales)
                                     v
                                  [historico]

No existe estado "borrada". Nunca se hace DELETE en operaciones de negocio.

## 11. Puntos de extension futuros

- **Smoke / Ping Pong:** cuando se aclare que son, agregar tabla conceptos o tratarlos como productos/servicios según corresponda.
- **Comisiones por servicio individual:** agregar tabla comisiones_config con barbero + servicio + pct + vigencia.
- **Autenticacion:** agregar tabla usuarios + middleware Flask antes de exponer a red pública.
- **Respaldos automáticos:** script cron + almacenamiento externo.
- **Bootstrap/UI:** reemplazar app.css por framework o template admin.