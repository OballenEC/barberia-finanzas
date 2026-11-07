# Lista de Evidencias para Portafolio y Entrevistas

Este documento es una guía interna para recopilar el material visual y técnico que demuestre la autoría y calidad del proyecto.

## 1. Capturas de Pantalla (Para el Portafolio)
- [ ] **Dashboard principal** (Vista Desktop y Mobile).
- [ ] **Formulario de registro** (mostrando la selección de barbero y cálculo de comisión).
- [ ] **Listado de inventario** (mostrando alertas de stock y costo promedio).
- [ ] **Reporte semanal** (mostrando la tabla comparativa y desglose por barbero).
- [ ] **Pantalla de validación/error** (ej. intentar vender sin stock o anular sin motivo).

## 2. Fragmentos de Código Clave (Para GitHub o Entrevistas)
- [ ] **El motor del CPM:** El archivo `app/domain/inventario.py` (mostrando la función `_replay_cpm`).
- [ ] **El modelo de datos:** El archivo `app/data/schema.sql` (mostrando las restricciones `CHECK` y llaves foráneas).
- [ ] **Lógica de reportes:** El archivo `app/reports/panel.py` (demostrando la separación de responsabilidades).

## 3. Evidencias de Pruebas (QA)
- [ ] **Captura de terminal:** Corriendo `python -m pytest tests/ -v` mostrando los `27 passed`.
- [ ] **Archivo de tests:** El archivo `tests/test_reports.py` (demostrando el test de "anti-doble-conteo").

## 4. Evidencias de Despliegue
- [ ] **URL en vivo:** Enlace a PythonAnywhere funcionando.
- [ ] **Captura de la consola de PythonAnywhere:** Mostrando la estructura de archivos o el `git pull`.

## 5. Documentos para Clientes
- [ ] **PDF de Ficha de Proyecto:** Exportar `FICHA_DE_PROYECTO.md` a PDF para enviarlo por correo.
- [ ] **Testimonio del Cliente:** (Pendiente de recopilar tras la entrega) Un breve audio o texto del dueño de la barbería diciendo que el sistema funciona.