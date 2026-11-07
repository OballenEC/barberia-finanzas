# Ficha de Proyecto: Sistema de Control Financiero para Barbería

## 📌 Descripción Ejecutiva
Aplicación web integral (mobile-first) desarrollada para digitalizar y automatizar las operaciones financieras de una barbería local. Transforma un proceso manual propenso a errores en un sistema centralizado que calcula márgenes reales, comisiones e inventario en tiempo real.

## 🎯 Necesidad Identificada
El negocio operaba con un cuaderno físico. Esto generaba tres problemas críticos:
1. Pérdida de tiempo diaria calculando comisiones y cortes semanales.
2. Desconocimiento del margen de ganancia real por producto (mezclando el costo de compra con la ganancia).
3. Falta de respaldo de datos y dificultad para auditar errores o fraudes.

## 💡 Solución Desarrollada
Un sistema web responsivo que centraliza la operación. El dueño puede registrar cortes, ventas y gastos desde su celular. El sistema hace los cálculos financieros automáticamente y protege la información mediante un historial inmutable.

## ⚙️ Funcionalidades Principales
- **Dashboard Financiero:** Panel con ingresos brutos, costos de venta (COGS), gastos y resultado neto.
- **Gestión de Barberos:** Registro de cortes con cálculo automático de comisiones (35%/40% configurable).
- **Inventario Inteligente:** Control de stock mediante compras y ventas. Uso de Costo Promedio Ponderado Móvil (CPM).
- **Auditoría (Anulaciones):** Los registros nunca se borran, se anulan con motivo, asegurando la trazabilidad de todas las operaciones.
- **Reportes Automatizados:** Generación de cortes diarios, semanales y de rendimiento individual por barbero.

## 💻 Tecnologías Utilizadas
- **Backend:** Python (v3.12) + Flask + Jinja2.
- **Base de Datos:** SQLite (Diseño relacional y transaccional).
- **Frontend:** HTML5, CSS3, Bootstrap 5 (Tema vintage responsivo).
- **QA / Testing:** Pytest (27 pruebas automatizadas).

## 📈 Beneficios Operativos Potenciales
- **Ahorro de tiempo:** Reducción drástica del tiempo dedicado a cuadres de caja y comisiones manuales.
- **Toma de decisiones:** Visibilidad clara de qué productos dejan mayor margen y cuáles no.
- **Control de mermas:** Registro estricto de inventario que reduce pérdidas.

## 👨‍💻 Mi Participación
**Desarrollo Full-Stack Integral.** Fui responsable del diseño de la base de datos, la arquitectura de software, la implementación de la lógica de negocio (CPM y comisiones), el diseño de la interfaz de usuario y el despliegue en el servidor en la nube. 

## 📊 Estado Real del Proyecto
**MVP Funcional y Desplegado.** El sistema se encuentra operativo con una URL en vivo. Cuenta con documentación técnica completa, 27 pruebas automatizadas pasando en verde, y está listo para escalar a fase de producción con clientes reales.

---
*Desarrollado por Oscar Esteban Ballen Castellanos - Estudiante de Ingeniería (UNAM) | Especialización Python (U-Michigan).*