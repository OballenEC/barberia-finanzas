# Modelo de datos

Fuente de verdad: `app/data/schema.sql`. Este documento explica el propsito de cada tabla y sus relaciones.

## 1. Diagrama de relaciones (textual)

    servicios <---- ventas_servicio ----> barberos
                          |
                          +-- anulada_por_id (self-FK)

    productos <---- compras_inventario
        ^
        +---- ventas_producto ----> barberos
        +---- ajustes_inventario
        +---- movimientos_inventario (histrico, no usado en cálculos)

    gastos_operativos (aislada, sin FK)

## 2. Entidades

### 2.1 servicios
Catlogo de servicios ofrecidos (Corte, Barba, Corte + Barba).

| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK | AUTOINCREMENT |
| nombre | TEXT UNIQUE | Nombre del servicio |
| precio_sugerido | TEXT (Decimal) | Precio base; el precio real se ingresa al registrar |
| activo | INTEGER 0/1 | Para retirar servicios sin borrarlos |
| seed_key | TEXT UNIQUE | Identifica datos demo; NULL en produccin |

### 2.2 barberos
Catlogo de barberos activos.

| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK | |
| nombre | TEXT UNIQUE | |
| comision_pct_default | TEXT (Decimal) | 35.00 o 40.00 por defecto; override al registrar |
| activo | INTEGER 0/1 | |
| seed_key | TEXT UNIQUE | |

### 2.3 ventas_servicio
Registro de cada corte o servicio vendido.

| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK | |
| servicio_id | FK -> servicios | |
| barbero_id | FK -> barberos, NULL | Opcional: servicios sin barbero no generan comisión |
| fecha_hora | TEXT (ISO-8601) | YYYY-MM-DDTHH:MM:SS |
| precio_cobrado | TEXT (Decimal) | Lo que realmente se cobr |
| metodo_pago | TEXT | efectivo/tarjeta/transferencia/otro |
| comision_pct | TEXT (Decimal) NULL | **Snapshot** del % aplicado |
| comision_monto | TEXT (Decimal) NULL | **Snapshot** del monto calculado |
| estado | TEXT | valida o anulada |
| anulada_por_id | FK self NULL | Trazabilidad si se reemplaz por otra venta |
| motivo_anulacion | TEXT NULL | Obligatorio si estado = anulada |
| creado_en | TEXT | Timestamp de creacin |
| seed_key | TEXT UNIQUE | |

**Regla:** comision_pct y comision_monto se congelan al momento del INSERT. Nunca se recalculan.

### 2.4 gastos_operativos
Gastos del negocio que no son producto para revender.

| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK | |
| fecha | TEXT | YYYY-MM-DD |
| descripción | TEXT | |
| categoria | TEXT | renta/servicios/insumos/otro |
| importe | TEXT (Decimal) | > 0 |
| metodo_pago | TEXT | |
| estado | TEXT | valida o anulada |
| motivo_anulacion | TEXT NULL | |
| creado_en | TEXT | |
| seed_key | TEXT UNIQUE | |

### 2.5 productos
Catlogo de productos con stock y costo calculado.

| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK | |
| nombre | TEXT | |
| codigo_interno | TEXT UNIQUE NULL | SKU opcional |
| costo_promedio | TEXT (Decimal) | Calculado por _replay_cpm. NO se edita manualmente |
| precio_venta | TEXT (Decimal) | |
| stock_actual | INTEGER | Calculado. CHECK >= 0 |
| activo | INTEGER 0/1 | |
| seed_key | TEXT UNIQUE | |

**Invariante:** stock_actual y costo_promedio se derivan de compras_inventario, ventas_producto y ajustes_inventario. Nunca se editan a mano.

### 2.6 compras_inventario
Registro de mercanca adquirida.

| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK | |
| fecha | TEXT | YYYY-MM-DD |
| producto_id | FK -> productos | |
| cantidad | INTEGER | CHECK > 0 |
| costo_unitario | TEXT (Decimal) | |
| total | TEXT (Decimal) | cantidad * costo_unitario, calculado |
| estado | TEXT | valida o anulada |
| motivo_anulacion | TEXT NULL | |
| creado_en | TEXT | |
| seed_key | TEXT UNIQUE | |

**Regla de negocio:** No se puede anular una compra si existen ventas posteriores del mismo producto. Esto protege el COGS histrico.

### 2.7 ventas_producto
Registro de cada venta de producto.

| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK | |
| fecha | TEXT | YYYY-MM-DD |
| producto_id | FK -> productos | |
| barbero_id | FK -> barberos, NULL | Opcional |
| cantidad | INTEGER | CHECK > 0 |
| precio_unitario | TEXT (Decimal) | |
| total_venta | TEXT (Decimal) | cantidad * precio_unitario |
| costo_unitario_snapshot | TEXT (Decimal) | **CPM congelado al momento de la venta** |
| costo_total_snapshot | TEXT (Decimal) | cantidad * costo_unitario_snapshot |
| comision_pct | TEXT (Decimal) NULL | Snapshot |
| comision_monto | TEXT (Decimal) NULL | Snapshot |
| estado | TEXT | valida o anulada |
| motivo_anulacion | TEXT NULL | |
| creado_en | TEXT | |
| seed_key | TEXT UNIQUE | |

**Regla crtica:** costo_unitario_snapshot NO cambia aunque el costo del producto suba después. Este es el corazn del sistema: el COGS histrico es inmutable.

### 2.8 ajustes_inventario
Correcciones manuales de stock con motivo obligatorio.

| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK | |
| fecha | TEXT | YYYY-MM-DD |
| producto_id | FK -> productos | |
| cantidad_delta | INTEGER | Positivo = aumenta, negativo = reduce. CHECK != 0 |
| motivo | TEXT NOT NULL | Obligatorio: merma, robo, corrección, etc. |
| usuario | TEXT NULL | En MVP no se usa (sin auth) |
| creado_en | TEXT | |
| seed_key | TEXT UNIQUE | |

**Uso típico:** corregir stock sin poder anular una compra bloqueada. Por ejemplo, "merma por producto daado" resta 1 unidad.

### 2.9 movimientos_inventario
Libro mayor histrico de movimientos. **No se usa para cálculos actuales** (ver nota).

| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK | |
| fecha | TEXT | |
| producto_id | FK -> productos | |
| tipo | TEXT | compra/venta/ajuste_positivo/ajuste_negativo/anulacion_compra/anulacion_venta |
| cantidad | INTEGER | |
| costo_unitario | TEXT (Decimal) | |
| referencia_tipo | TEXT | compra_inventario/venta_producto/ajuste_manual |
| referencia_id | INTEGER | |
| motivo | TEXT NULL | |
| creado_en | TEXT | |

**Nota:** Esta tabla se conserva como bitcora histrica. El cálculo actual de stock y CPM se hace con _replay_cpm() leyendo directamente las tablas origen (compras, ventas, ajustes) filtradas por estado='valida'. Evita duplicacin de efectos al anular.

## 3. Relaciones resumidas

- servicios 1--N ventas_servicio
- barberos 1--N ventas_servicio (opcional)
- barberos 1--N ventas_producto (opcional)
- productos 1--N compras_inventario
- productos 1--N ventas_producto
- productos 1--N ajustes_inventario
- productos 1--N movimientos_inventario
- ventas_servicio es autoreferencial (anulada_por_id)
- gastos_operativos no tiene FK

## 4. Convenciones de datos

- **Importes:** TEXT con formato "1234.50", parseados a Decimal en Python.
- **Estados:** 'valida' o 'anulada'. Nunca se borra una fila.
- **Snapshot:** todo campo que pueda cambiar con el tiempo (costo, comisión %) se congela en la fila al INSERT.
- **Seed key:** presente en tablas con datos demo. NULL en produccin.
- **Fechas:** DATE para columnas de fecha, DATETIME para fecha_hora de servicios.
- **Timestamps:** creado_en se llena con datetime.now().isoformat(timespec="seconds").

## 5. Invariantes del sistema

1. stock_actual = SUM(compras validadas) - SUM(ventas validadas) + SUM(ajustes)
2. costo_promedio = CPM según _replay_cpm cronológico
3. ventas_producto.costo_unitario_snapshot = CPM al momento de la venta
4. ventas_servicio.comision_monto = precio_cobrado * comision_pct / 100
5. Ningn campo de snapshot cambia después del INSERT
6. Toda anulación tiene motivo_anulacion no vaco