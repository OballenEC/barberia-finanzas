# Requisitos y supuestos

Documento vivo. Distingue entre:
- Lo **confirmado** por el cliente.
- Lo **asumido** provisionalmente mientras se confirma.
- Lo **pendiente** de aclaracin antes de uso en produccin.

## 1. Contexto del cliente

Dueo de una barbería que actualmente lleva sus cuentas en un cuaderno fsico.

Procedimiento actual (identificado en audio/video de WhatsApp):
- Anota operaciones manualmente.
- Obtiene totales diarios y acumula para el cierre semanal.
- Realiza su corte semanal los **domingos**.
- Distingue: total de cortes y servicios, total de productos, total de "Smoke", total de "Ping Pong", mercanca y gastos.

## 2. Requisitos confirmados

| # | Requisito | Mdulo |
|---|---|---|
| R1 | Registrar ingresos por servicios de barbería | Servicios |
| R2 | Registrar gastos operativos | Gastos |
| R3 | Registrar compras de productos | Inventario |
| R4 | Registrar ventas de productos | Ventas |
| R5 | Consultar y actualizar inventario con stock y costo promedio | Productos/Inventario |
| R6 | Registrar el barbero que realiz el servicio | Servicios/Barberos |
| R7 | Calcular automticamente la comisión (35% o 40%) | Servicios/Barberos |
| R8 | Calcular comisiones por venta de productos | Ventas/Barberos |
| R9 | Distinguir comisiones por servicios, comisiones por productos, ingresos por servicios, ingresos por productos | Reportes |
| R10 | Obtener cierre semanal con referencia al domingo | Reportes |
| R11 | Interfaz adaptable a celular y computadora | UI |
| R12 | Persistencia de datos tras cerrar y reabrir la app | BD |
| R13 | Reportes diario y semanal consultables | Reportes |
| R14 | Reporte por barbero (servicios, comisiones, productos) | Reportes |

## 3. Supuestos provisionales

Supuestos que **sostienen el MVP** y que deben validarse con el cliente antes de uso en produccin:

| # | Supuesto | Impacto si es falso |
|---|---|---|
| S1 | Registro en orden cronológico (compras antes de ventas del mismo producto) | Snapshot de costo histrico puede diferir del real |
| S2 | % de comisión por defecto: 35% (override a 40% al registrar) | Requiere ajuste en formularios y seed |
| S3 | La comisión de producto se calcula como % del precio de venta | Si es % del margen, cambia la frmula |
| S4 | Semana lunesdomingo, cierre dominical al final del día | Cambio en rangos de fecha de reportes |
| S5 | Compras de inventario NO restan del resultado (solo COGS) | Es la regla contable estndar; si el cliente quiere restar compras, cambia el modelo |
| S6 | Una venta de producto sin barbero asignado no genera comisión | Si toda venta debe atribuirse, se requiere asignación obligatoria |
| S7 | Sin impuestos (IVA/ISR) en el MVP | Resultado neto no ser utilidad fiscal |
| S8 | Sin propinas ni devoluciones | Ingresos netos pueden sobreestimarse |
| S9 | Un solo "almacn" (sin sucursales) | Requiere rediseo si crece |
| S10 | Un solo usuario (dueo) sin login | No apto para red pública sin auth |

## 4. Preguntas pendientes para el cliente

Prioridad: **(BI)** bloquea implementación  **(UR)** bloquea uso real, no demo.

| # | Pregunta | Prioridad |
|---|---|---|
| P1 | Qu determina si un barbero recibe 35% o 40%? Es fijo por barbero, por tipo de servicio, antigedad, metas? | BI |
| P2 | La comisión de productos es % del precio de venta, % del margen, monto fijo, u otra frmula? | BI |
| P3 | La comisión por producto se paga solo cuando ese barbero vendi, o siempre se atribuye a alguien? | BI |
| P4 | Qu significa exactamente "Smoke"? Es producto, servicio, renta u otro? | BI |
| P5 | Qu significa exactamente "Ping Pong"? Es producto, servicio, renta u otro? | BI |
| P6 | El periodo semanal es lunesdomingo (cierra domingo al final) o domingosbado? | BI |
| P7 | Las comisiones se pagan al cierre semanal o al momento de cada venta? | UR |
| P8 | Hay propinas? Son para el barbero o para el negocio? | UR |
| P9 | Hay devoluciones o cambios de producto? | UR |
| P10 | Los barberos trabajan por turnos que afectan a quin se atribuye una venta? | UR |
| P11 | Qu métodos de pago se manejan en la práctica? | UR |
| P12 | Hay ms de una sucursal o solo el local actual? | UR |

## 5. Fuera del alcance del MVP

Explcitamente **no incluido** en esta entrega:

- Autenticacin con usuario y contrasea.
- Roles y permisos diferenciados.
- Multi-sucursal.
- Facturacin electrnica (CFDI).
- Impuestos (IVA/ISR).
- Nmina de barberos.
- Integracin con terminales de pago.
- App nativa Android/iOS.
- Notificaciones push.
- Respaldos automáticos a la nube.
- Modelado de "Smoke" y "Ping Pong".

Estos pueden considerarse en fases posteriores con cotizacin separada.

## 6. Criterios de aceptacin por módulo

### Servicios
- [x] Se puede registrar un servicio con fecha, barbero, precio y método de pago.
- [x] El sistema calcula la comisión automticamente.
- [x] Se puede anular con motivo obligatorio (auditable).
- [x] Un servicio anulado no suma a totales pero permanece en historial.

### Gastos
- [x] Registro con descripción, categora, importe, método de pago y fecha.
- [x] Anulacin auditable con motivo.
- [x] Gastos se separan de compras de inventario.

### Productos e inventario
- [x] Catlogo con nombre, código, precio de venta.
- [x] Compras aumentan stock y recalculan CPM.
- [x] Ventas descuentan stock y congelan snapshot de costo.
- [x] Venta con stock insuficiente se rechaza.
- [x] Anulacin de compra bloqueada si hay ventas posteriores.
- [x] Ajuste manual con motivo obligatorio.

### Ventas de producto
- [x] Atribucin opcional a barbero con comisión congelada.
- [x] Anulacin reintegra stock y excluye COGS del reporte.

### Reportes
- [x] Panel con KPIs separados (ingresos, ventas, gastos, compras, COGS, comisiones, margen, resultado neto, flujo).
- [x] Reporte diario con detalle de operaciones del día.
- [x] Reporte semanal con comparacin semana anterior.
- [x] Reporte por barbero con desglose individual.
- [x] Anti-doble-conteo: compras NO restan del resultado.

### Persistencia
- [x] Datos sobreviven a reiniciar la app.
- [x] Seed idempotente (ejecutar dos veces no duplica).