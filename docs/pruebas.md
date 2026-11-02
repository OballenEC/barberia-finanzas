# Plan y resultados de pruebas

Suite automatizada con pytest. 27 tests, todos pasando.

Comando de ejecución:

    python -m pytest tests/ -v

Resultado observado (última ejecución):

    27 passed in 3.05s

## 1. Cobertura por módulo

| Archivo | Tests | Qu valida |
|---|---|---|
| tests/test_servicios.py | 7 | Servicios, comisiones, redondeo, validaciones, anulación |
| tests/test_inventario.py | 7 | CPM, snapshots, stock insuficiente, bloqueo de anulación, reintegro |
| tests/test_reports.py | 6 | Frmulas financieras, anti-doble-conteo, rangos de fecha, filtros |
| tests/test_anulaciones.py | 5 | Anulacin auditable en servicios, gastos, ventas producto |
| tests/test_persistencia.py | 2 | Persistencia entre conexiones, seed idempotente |
| **Total** | **27** | |

## 2. Detalle de pruebas por archivo

### tests/test_servicios.py (7 tests)

1. **test_registrar_servicio_sin_barbero**
   - Escenario: registrar Corte $100 sin asignar barbero.
   - Esperado: precio guardado, barbero_id NULL, sin comisión.
   - Resultado: PASSED.

2. **test_registrar_servicio_con_barbero_default**
   - Escenario: Corte $100 con Luis (35%).
   - Esperado: comision_pct=35.00, comision_monto=35.00.
   - Resultado: PASSED.

3. **test_registrar_servicio_con_override_pct**
   - Escenario: Corte + Barba $150 con Juan (35% default), override 40%.
   - Esperado: comision_pct=40.00, comision_monto=60.00.
   - Resultado: PASSED.

4. **test_comision_redondeo_correcto**
   - Escenario: $33.33 al 35%.
   - Esperado: comision_monto=11.67 (HALF_UP de 11.6655).
   - Resultado: PASSED.

5. **test_precio_negativo_rechazado**
   - Escenario: precio_cobrado=-50.
   - Esperado: ValueError.
   - Resultado: PASSED.

6. **test_anular_venta_servicio**
   - Escenario: anular servicio con motivo, luego intentar anular de nuevo.
   - Esperado: primera anulación OK, segunda lanza ValueError.
   - Resultado: PASSED.

7. **test_anular_sin_motivo_falla**
   - Escenario: anular con motivo vaco.
   - Esperado: ValueError.
   - Resultado: PASSED.

### tests/test_inventario.py (7 tests)

1. **test_compra_aumenta_stock_y_cpm**
   - 10 uds a $80  stock 10, CPM $80.
   - PASSED.

2. **test_segunda_compra_recalcula_cpm_ponderado**
   - 10@$80 + 10@$100  stock 20, CPM $90.
   - PASSED.

3. **test_venta_descuenta_stock_y_congela_snapshot**
   - Venta de 2 uds con CPM $80  snapshot congelado $80, stock 8.
   - PASSED.

4. **test_snapshot_inmutable_a_compras_futuras**
   - Comprar ms caro después NO altera el snapshot de la venta previa.
   - PASSED.

5. **test_venta_sin_stock_falla**
   - Vender 10 con stock 5  ValueError "Stock insuficiente".
   - PASSED.

6. **test_anular_compra_con_venta_posterior_bloqueado**
   - La regla clave: intentar anular compra con ventas posteriores  ValueError.
   - PASSED.

7. **test_anular_venta_reintegra_stock**
   - Anular venta devuelve stock (de 7 a 10).
   - PASSED.

### tests/test_reports.py (6 tests)

1. **test_panel_formulas_completas**
   - Escenario controlado con servicio + venta producto + gasto.
   - Verifica: ingresos, ventas, gastos, compras, COGS, margen, comisiones, resultado neto, flujo.
   - Valores esperados: ingresos=$100, ventas=$300, COGS=$160, comisiones=$140, resultado=-$150, flujo=-$790.
   - PASSED.

2. **test_anti_doble_conteo_compras_no_restan_del_resultado**
   - Regla clave: compras $800 NO restan del resultado. Si lo hicieran, sera -$950. Resultado real: -$150.
   - PASSED.

3. **test_reporte_diario_respeta_rango**
   - Da 1 solo incluye operaciones del día 1. Da 2 solo del día 2.
   - PASSED.

4. **test_reporte_semanal_compara_semana_anterior**
   - Semana actual con datos, anterior en cero.
   - PASSED.

5. **test_reporte_barbero_agrega_servicios_y_productos**
   - Reporte por barbero suma servicios + productos correctamente.
   - PASSED.

6. **test_reporte_barbero_filtra_por_id**
   - Si se pide un barbero específico, no devuelve otros.
   - PASSED.

### tests/test_anulaciones.py (5 tests)

1. **test_anular_servicio_lo_excluye_de_totales**
   - Servicio anulado no suma al panel pero S queda en historial con motivo.
   - PASSED.

2. **test_anular_gasto_lo_excluye_de_totales**
   - Gasto anulado no suma al panel pero queda en historial.
   - PASSED.

3. **test_anular_venta_producto_reintegra_stock_y_excluye_cogs**
   - Anular venta: stock vuelve, COGS=0 en reporte.
   - PASSED.

4. **test_anular_dos_veces_falla**
   - Segunda anulación lanza ValueError.
   - PASSED.

5. **test_anular_sin_motivo_falla_en_todos_los_modulos**
   - Motivo vaco rechazado en servicios, gastos, compras, ventas.
   - PASSED.

### tests/test_persistencia.py (2 tests)

1. **test_datos_persisten_entre_conexiones**
   - Registrar venta, cerrar conexin, abrir otra, verificar que sigue.
   - PASSED.

2. **test_seed_idempotente_no_duplica**
   - init_schema dos veces no duplica tablas. INSERT OR IGNORE no duplica filas.
   - PASSED.

## 3. Notas técnicas

### Aislamiento
Cada test usa su propio archivo SQLite en `tempfile.mkdtemp()`, eliminado al final. Los tests no interfieren entre s.

### Sin Flask
Los tests prueban `domain/` y `reports/` directamente con una conexin limpia. No levantan servidor web. Esto los hace rpidos (~3s para 27 tests).

### Windows y file handles
SQLite en Windows mantiene file handles abiertos un tiempo. Los tests de persistencia usan `gc.collect()` + `shutil.rmtree(ignore_errors=True)` para evitar `PermissionError`.

### Fixtures
- `conn`: BD con schema + catlogos demo (servicios y productos).
- `conn_vacia`: BD solo con schema.
- `helpers`: funciones utilitarias (get_id_servicio, get_id_producto, crear_barbero).

## 4. Pruebas que NO estn cubiertas (limitacin conocida)

Las siguientes áreas no tienen test automatizado todava:

- Formularios HTML end-to-end (requiere Selenium o Playwright).
- Rutas Flask con request/response completa.
- Clculo de CPM cuando hay anulación de venta seguida de nueva compra del mismo día.
- Reportes con rango vaco (semana sin operaciones) ya esté cubierto por kpis_anterior en cero.
- Concurrencia (dos usuarios al mismo tiempo).

Estas quedan para Fase 5+ si el cliente lo requiere.

## 5. Cmo aadir un test nuevo

1. Crear archivo `tests/test_<modulo>.py`.
2. Usar fixture `conn` o `conn_vacia` de `conftest.py`.
3. Importar la función de `app.domain` o `app.reports` a probar.
4. Un test por escenario. Nombre descriptivo: `test_<que_hace>_<resultado_esperado>`.
5. Ejecutar: `python -m pytest tests/test_<modulo>.py -v`.

## 6. Historial de ejecuciones

| Fecha | Test count | Resultado | Duracin |
|---|---|---|---|
| 2026-11-02 | 27 | 27 passed | 3.05s |
| 2026-11-02 | 27 | 27 passed (tras fix Windows) | 3.04s |
| 2026-11-02 | 27 | 27 passed (final) | 3.08s |

Verificacin reproducible: `python -m pytest tests/ -v`.