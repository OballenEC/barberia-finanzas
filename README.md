# 🪒 Sistema Web de Control Financiero y Operativo para Barbería

Aplicación web responsiva (mobile-first) diseñada para digitalizar y automatizar las finanzas de una barbería real. Reemplaza el registro manual en cuaderno por un sistema en la nube con cálculo de inventario, comisiones y reportes diarios/semanales.

🔗 **Demo en vivo:** [https://OballenEC.pythonanywhere.com](https://OballenEC.pythonanywhere.com) *(MODO DEMO - Datos ficticios)*

## 📋 El Problema
El dueño de la barbería llevaba sus cuentas a mano, lo que dificultaba conocer su rentabilidad real (margen de productos), calcular las comisiones de sus barberos y mantener un control de inventario preciso sin perder datos históricos.

## 🛠️ Solución y Funcionalidades Principales
- **Panel de Control (Dashboard):** Visualización de ingresos, ventas, gastos, costos de venta (COGS) y resultado neto estimado al instante.
- **Servicios y Barberos:** Registro de cortes con asignación de barbero y cálculo automático de comisiones (35% o 40%, configurable por venta).
- **Inventario y Ventas:** Catálogo de productos con alertas de stock. Cálculo de **Costo Promedio Ponderado Móvil (CPM)**.
- **Histórico Inmutable:** Anulaciones auditables. Si se anula una operación, no se borra de la base de datos; queda marcada como "anulada" con un motivo, protegiendo la integridad financiera.
- **Reportes:** Cierres diarios, semanales y desglose de rendimiento por cada barbero.

## 💻 Stack Tecnológico
- **Backend:** Python 3, Flask, Jinja2.
- **Base de Datos:** SQLite (Uso de `Decimal` en formato TEXT para evitar errores de flotantes en finanzas).
- **Frontend:** HTML5, CSS3, Bootstrap 5 (Tema vintage personalizado), Bootstrap Icons.
- **Pruebas:** Pytest (27 tests automatizados pasando).

## 🏗️ Arquitectura del Proyecto
El código sigue una separación estricta de responsabilidades (Clean Architecture):
- `app/domain/`: Reglas de negocio puras (cálculos de comisiones, lógica del CPM, validaciones).
- `app/data/`: Repositorios y conexión a SQLite.
- `app/reports/`: Lógica de consultas financieras (separada del acceso a datos).
- `app/web/`: Rutas de Flask y controladores.
- `app/templates/`: Interfaz visual (Jinja2).

## 🚀 Instalación y Ejecución Local

1. Clonar el repositorio:
   `git clone https://github.com/OballenEC/barberia-finanzas.git`
2. Crear y activar el entorno virtual:
   `python -m venv .venv`
   `.venv\Scripts\activate` (Windows)
3. Instalar dependencias:
   `pip install -r requirements.txt`
4. Inicializar la base de datos y cargar datos de prueba:
   `python -m scripts.init_db`
   `python -m scripts.seed_demo`
5. Ejecutar la aplicación:
   `python run.py`

## 🧪 Pruebas Automatizadas
Para verificar la precisión de los cálculos financieros e inventario:
`python -m pytest tests/ -v`
*(Resultado esperado: 27 passed)*

## 📸 Capturas de Pantalla
*(Añadir próximamente capturas del Dashboard, Inventario y Reportes aquí)*

## ⚠️ Limitaciones Conocidas y Roadmap
- **Autenticación:** Actualmente no cuenta con sistema de login (diseñado para uso local o intranet).
- **Módulos pendientes:** Integración de los conceptos "Smoke" y "Ping Pong" (en espera de definición exacta del cliente).
- **Escalabilidad:** SQLite es suficiente para el volumen actual. Si el negocio crece a múltiples sucursales, se migrará a PostgreSQL.

---
*Desarrollado por Oscar Esteban Ballen Castellanos - Estudiante de Ingeniería (UNAM), Especialización en Python (U-Michigan), 2do Lugar Hackathon.*