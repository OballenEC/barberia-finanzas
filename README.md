# Barbería · Sistema de Control Financiero

Aplicación web adaptable a celular y computadora para registrar las operaciones diarias de una barbería y consultar reportes financieros.

Construida en Python + Flask + SQLite con interfaz mobile-first. Sin dependencias de pago, sin servicios externos, ejecutable en local o en hosting gratuito.

## Estado del proyecto

- **MVP funcional** en fase de entrega.
- 27 pruebas automatizadas, todas pasando.
- Documentación técnica completa en `docs/`.

## Funcionalidades

| Módulo | Qué hace |
|---|---|
| **Panel** | KPIs del periodo: ingresos, ventas, gastos, COGS, comisiones, margen bruto, resultado neto estimado, flujo de efectivo |
| **Servicios** | Registro de cortes con barbero, precio cobrado y comisión automática (35%/40% configurable) |
| **Gastos** | Registro de gastos operativos con categoría, importe y método de pago |
| **Productos** | Catálogo con costo promedio ponderado móvil (CPM) y stock calculado |
| **Inventario** | Compras (aumentan stock), ajustes con motivo obligatorio, anulaciones auditables |
| **Ventas de producto** | Descuento automático de stock + snapshot de costo por venta |
| **Barberos** | Alta con % de comisión por defecto, override por venta |
| **Reportes** | Panel, diario, semanal (con comparación), por barbero |

## Decisiones técnicas destacadas

1. **Costo Promedio Ponderado Móvil (CPM) con snapshot por venta.**
   El COGS histórico es inmutable: si el costo de un producto sube después, el reporte de la venta pasada no cambia.

2. **Snapshot del % de comisión por cada venta.**
   Cambiar el % de un barbero no altera las comisiones de semanas anteriores.

3. **Anulaciones auditables con motivo obligatorio.**
   Nada se borra. Toda operación anulada queda en historial y se excluye de totales, pero permanece visible.

4. **Anti-doble-conteo financiero.**
   Las compras de inventario **no** restan del resultado. Solo se descuenta el costo de lo efectivamente vendido (COGS).

5. **Separación estricta de conceptos.**
   Ingresos por servicios ≠ ventas de productos ≠ gastos operativos ≠ compras de inventario ≠ COGS ≠ comisiones ≠ flujo de efectivo ≠ resultado neto.

6. **Arquitectura por capas.**
   `app/domain/` (reglas de negocio), `app/data/` (acceso a datos), `app/reports/` (cálculos financieros), `app/web/` (rutas y orquestación). Los dominios no importan Flask ni SQL directo.

## Stack técnico

- Python 3.12+
- Flask 3.0
- SQLite (con `Decimal`-as-TEXT para evitar errores de flotantes)
- Jinja2
- HTML/CSS mobile-first
- pytest (27 tests)
- Git + GitHub

## Instalación local

Requisitos: Python 3.12 o superior, Git.

Pasos:

1. Clonar el repositorio:
   git clone https://github.com/OballenEC/barbería-finanzas.git
   cd barbería-finanzas

2. Crear entorno virtual:
   python -m venv .venv

3. Activar el entorno virtual:

   Windows:
   .venv\Scripts\activate

   Linux/Mac:
   source .venv/bin/activate

4. Instalar dependencias:
   pip install -r requirements.txt

5. Copiar variables de entorno:

   Windows:
   copy .env.example .env

   Linux/Mac:
   cp .env.example .env

6. Inicializar la base de datos:
   python -m scripts.init_db

7. Cargar datos de demostración:
   python -m scripts.seed_demo

8. Arrancar la aplicación:
   python run.py

Abre `http://127.0.0.1:5000` en el navegador.

## Pruebas

Ejecuta la suite completa:

    python -m pytest tests/ -v

Resultado esperado: 27 passed.

Archivos de prueba y qué validan:

- tests/test_servicios.py — Registro de servicios, comisiones, redondeo, validaciones
- tests/test_inventario.py — CPM, snapshots, ventas sin stock, bloqueo de anulación
- tests/test_reports.py — Fórmulas financieras, anti-doble-conteo, rangos de fecha
- tests/test_anulaciones.py — Anulación auditable en todos los módulos
- tests/test_persistencia.py — Persistencia entre reinicios, seed idempotente

## Estructura del proyecto

    barbería-finanzas/
    ├── app/
    │   ├── config.py
    │   ├── domain/
    │   ├── data/
    │   │   ├── schema.sql
    │   │   ├── seed_demo.sql
    │   │   └── repositories/
    │   ├── reports/
    │   ├── web/
    │   ├── templates/
    │   └── static/
    ├── scripts/
    │   ├── init_db.py
    │   └── seed_demo.py
    ├── tests/
    ├── docs/
    ├── instance/
    ├── run.py
    ├── requirements.txt
    └── README.md

## Datos de demostración

El script `scripts/seed_demo.py` carga un escenario reproducible con:

- 2 barberos (Luis 35%, Juan 40%)
- 3 servicios de barbería (Corte, Barba, Corte + Barba)
- 3 productos con distintos costos
- Compras de inventario, ventas de producto y ajuste justificado
- Gastos operativos
- Operaciones distribuidas en una semana

Los datos son **claramente ficticios** y aparecen con un banner amarillo en la interfaz identificándolos como MODO DEMO.

Ejecutar dos veces `python -m scripts.seed_demo` no duplica registros (idempotencia por `seed_key`).

## Limitaciones conocidas

- **Sin autenticación.** Es un MVP para uso local o en red privada.
- **Sin respaldos automáticos.** Se documenta procedimiento manual en `docs/manual_usuario.md`.
- **Smoke y Ping Pong** no están modelados todavía. Pendiente de aclaración con el cliente.
- **UI básica.** Funcional, sin framework de diseño. Mejora planificada para fase posterior.
- **Asume registro cronológico.** Registrar ventas pasadas después de compras futuras del mismo producto no recalcula snapshots históricos automáticamente.
- **Un solo usuario por sesión.** No hay roles ni permisos diferenciados.

## Roadmap

- [x] Fase 1 — Diseño (modelo, reglas, supuestos)
- [x] Fase 2 — Esqueleto Flask + SQLite
- [x] Fase 3 — Operaciones (servicios, gastos, productos, inventario)
- [x] Fase 3.4 — Barberos + comisiones con snapshot
- [x] Fase 4 — Reportes (panel, diario, semanal, por barbero)
- [x] Fase 6 — 27 pruebas automatizadas
- [x] Fase 7 — Documentación
- [ ] Fase 5 — Deploy + capacitación al cliente
- [ ] Fase 8 — Mejora visual con Bootstrap

## Autor

**OballenEC** — Estudiante de Ingeniería en Telecomunicaciones, Sistemas y Electrónica (UNAM).

- Especialización Python (Universidad de Michigan · Coursera)
- 2do lugar en hackathon
- Desarrollador full-stack junior freelance

Contacto: [GitHub](https://github.com/OballenEC)

## Licencia

Proyecto privado. Cliente real en producción. Código disponible para revisión bajo solicitud.