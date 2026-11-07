# Documentación Técnica del Sistema

Este documento detalla las decisiones arquitectónicas, el modelo de datos y la lógica financiera implementada en el sistema de control para la barbería. Está orientado a demostrar la calidad técnica del desarrollo.

## 1. Arquitectura del Sistema (Clean Architecture)
Para garantizar la mantenibilidad y la capacidad de probar el código sin depender del framework web, el proyecto está dividido en capas estrictas:
- **Domain (`app/domain/`):** Contiene las reglas de negocio puras (cálculos de comisiones, validaciones de stock, lógica del CPM). No importa Flask, ni Jinja2, ni el módulo de SQLite. Es Python puro.
- **Data (`app/data/`):** Único punto de contacto con la base de datos. Contiene los repositorios y el esquema SQL. Utiliza consultas parametrizadas (protección contra inyección SQL).
- **Reports (`app/reports/`):** Lógica de lectura y cálculo de KPIs financieros. No modifica datos, solo consulta y agrega.
- **Web (`app/web/`):** Controladores de Flask. Reciben la petición HTTP, validan de forma superficial, delegan a la capa de dominio o reportes y devuelven la respuesta renderizada.

## 2. Modelo de Datos y Relaciones
La base de datos SQLite se diseñó para evitar la redundancia y garantizar la integridad referencial. Tablas principales:
- `servicios` y `barberos`: Catálogos base. Un barbero tiene un porcentaje de comisión por defecto (ej. 35%).
- `ventas_servicio`: Registro de cortes. Almacena el `precio_cobrado` y hace un **snapshot** del `comision_pct` y `comision_monto` aplicados. Si el barbero cambia de comisión mañana, el histórico no se altera.
- `productos`: Catálogo con `costo_promedio` (CPM) y `stock_actual`.
- `compras_inventario`: Entradas de mercancía. Al registrarse, se recalcula el CPM.
- `ventas_producto`: Salidas. Congela el `costo_unitario_snapshot` y `costo_total_snapshot` para el cálculo del COGS.
- `ajustes_inventario`: Mermas o correcciones manuales con motivo justificado.

## 3. Lógica Financiera y Contable (Lo más crítico)
El sistema evita el error clásico de "restar las compras de inventario de las ventas del día".
- **Costo Promedio Ponderado Móvil (CPM):** Cuando entra mercancía, se calcula: `(stock_actual * costo_promedio_actual + cantidad_nueva * costo_unitario_nuevo) / (stock_actual + cantidad_nueva)`.
- **Costo de Ventas (COGS):** Al vender un producto, se extrae el costo unitario (CPM del momento) y se multiplica por la cantidad vendida.
- **Resultado Neto Estimado:** Se calcula como `Ingresos (Servicios + Productos) - COGS - Gastos Operativos - Comisiones (Servicios + Productos)`.
- **Separación estricta:** Las compras de mercancía **NO** restan del resultado neto del día. Afectan el flujo de efectivo, pero el gasto real se reconoce cuando el producto se vende (a través del COGS).

## 4. Histórico Inmutable y Anulaciones Auditables
Ninguna operación financiera se borra físicamente de la base de datos (DELETE). 
- Si un administrador anula un corte, la fila cambia su estado a `anulada`, guarda el motivo y deja de sumar en los reportes, pero permanece visible en el historial. Esto previene fraudes o descuadres contables.
- **Protección de inventario:** No se permite anular una compra de mercancía si ya se han registrado ventas de ese producto. El sistema exige usar un "Ajuste de Inventario" para corregir el stock sin corromper los COGS históricos.

## 5. Manejo de Errores y Tipos de Datos
- **Precisión financiera:** Todo cálculo monetario utiliza la clase `Decimal` de Python (nunca `float`), para evitar errores de redondeo binario (ej. que 0.1 + 0.2 sea 0.30000000000000004). En SQLite, los importes se guardan como TEXT y se parsean a Decimal.
- **Transacciones atómicas:** El registro de una venta y la actualización del stock se ejecutan dentro de un bloque `with conn:` (commit/rollback automático). Si falla la actualización de stock, la venta no se guarda, previniendo datos huérfanos.
- **Validaciones de dominio:** El backend rechaza ventas si no hay stock suficiente, si el precio es negativo, o si se intenta registrar una comisión mayor al 100%.

## 6. Pruebas Automatizadas (Pytest)
El sistema cuenta con **27 pruebas automatizadas** que validan:
- Cálculo correcto del CPM con múltiples compras.
- Inmutabilidad de los snapshots (si sube el costo del producto, la venta pasada no cambia).
- Rechazo de ventas sin stock.
- Bloqueo de anulación de compras con ventas posteriores.
- Fórmulas de reportes (asegurando que las compras no resten del resultado neto).

## 7. Seguridad y Limitaciones Actuales
- Las consultas SQL están 100% parametrizadas.
- El servidor de desarrollo de Flask no se expone a internet; el despliegue en producción se realiza mediante WSGI en un servidor configurado (PythonAnywhere).
- **Limitación:** No cuenta con sistema de autenticación de usuarios (login) ya que fue diseñado como una herramienta interna para el dueño. Para una exposición pública masiva, se requeriría implementar Flask-Login.