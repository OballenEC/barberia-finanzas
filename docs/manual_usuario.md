# Manual de usuario

Guia rápida para el dueno de la barbería. Sin términos técnicos.

## Que es este sistema

Una aplicación web que abres en tu celular o computadora para llevar las cuentas diarias de la barbería: cortes, productos, gastos, comisiones, y ver cuanto ganaste de verdad.

## Como abrir la aplicación

1. Abre el navegador (Chrome, Edge o Safari).
2. Ve a la direccion que te dio tu desarrollador (ejemplo: http://127.0.0.1:5000 o https://barbería-xxx.pythonanywhere.com).
3. Veras la pantalla principal con un menu arriba.

**Nota:** si la barra amarilla dice "MODO DEMO", estás viendo datos de prueba. Tus datos reales no se tocan hasta que el desarrollador active el modo producción.

## Como registrar un corte

1. Toca "Servicios" en el menu.
2. Toca el boton "Registrar servicio".
3. Elige el tipo de servicio (Corte, Barba, Corte + Barba).
4. Elige el barbero que lo hizo.
5. Si el barbero cobra un porcentaje distinto al de costumbre, escribelo en "Comision %". Si no, dejalo vacio.
6. Escribe la fecha y hora (viene la de hoy automáticamente).
7. Escribe el precio que cobraste.
8. Elige como pago el cliente (efectivo, tarjeta, transferencia, otro).
9. Toca "Guardar".

La comisión del barbero se calcula automáticamente y queda registrada. Si manana cambias el porcentaje del barbero, los cortes de hoy no se modifican.

## Como registrar un gasto

1. Toca "Gastos" en el menu.
2. Toca "Registrar gasto".
3. Escribe la descripción (ej. "Renta de noviembre").
4. Escribe la categoria (renta, luz, insumos, otro).
5. Escribe el importe.
6. Elige el método de pago.
7. Toca "Guardar".

**Importante:** los gastos NO son lo mismo que comprar productos para vender. Si compras 10 ceras para vender, eso se registra en "Inventario", no en "Gastos".

## Como registrar una compra de productos

1. Toca "Inventario" en el menu.
2. Toca "Compra".
3. Elige el producto (o crealo primero en "Productos" si no existe).
4. Escribe cuantas unidades compraste.
5. Escribe cuanto pagaste por cada una.
6. Toca "Guardar".

El sistema actualiza solo el stock y el costo promedio del producto.

## Como registrar una venta de producto

1. Toca "Ventas" en el menu.
2. Toca "Registrar venta".
3. Elige el producto.
4. Escribe cuantas unidades vendiste.
5. Escribe a que precio vendiste cada una.
6. Toca "Guardar".

El sistema descuenta del stock automáticamente y guarda el costo del momento. Si manana el costo del producto sube, la ganancia de esta venta no cambia.

## Como ver cuanto gane hoy

1. Toca "Reportes" en el menu, luego "Reporte diario".
2. Selecciona la fecha.
3. Veras:
   - Cuanto entro por servicios
   - Cuanto entro por productos
   - Cuanto gastaste
   - Cuanto costaron los productos que vendiste
   - Cuanto pagaste de comisiones
   - **Cuanto te qued (resultado neto estimado)**

**Ojo:** el "resultado neto estimado" es una estimacion para que veas como va tu negocio, no es una declaracion fiscal. Para impuestos consulta a tu contador.

## Como ver el cierre semanal

1. Toca "Reportes" en el menu, luego "Reporte semanal".
2. Veras la semana actual y la anterior para comparar.
3. Al final, la tabla por barbero con cuanto vendio cada uno y cuanto gano de comisión.

Tu corte de caja es el domingo al final del día.

## Como ver cuanto gano cada barbero

1. Toca "Reportes" en el menu, luego "Reporte por barbero".
2. Elige la semana (o el barbero específico).
3. Veras por cada barbero:
   - Cuantos cortes hizo
   - Cuanto genero
   - Cuanto de comisión le toca
   - Cuantas ventas de producto hizo
   - Su total a pagar

## Como corregir un error

Si te equivocaste en algo (registraste un corte con precio equivocado, un gasto duplicado, etc.):

1. Ve al módulo donde esta el registro (Servicios, Gastos, Inventario o Ventas).
2. Busca el registro en la lista.
3. Toca "Anular" y escribe el motivo (obligatorio).
4. El registro deja de contar en los totales, pero queda en el historial para que siempre puedas revisar que paso.

**No existe la opcion de borrar.** Todo se conserva para que las cuentas sean confiables.

## Como corregir el stock de un producto

Si te falta producto (se rompio, te robaron, contaste mal):

1. Toca "Inventario" en el menu.
2. Toca "Ajuste".
3. Elige el producto.
4. Escribe la cantidad con signo negativo si quitas (ej. -1) o positivo si agregas.
5. Escribe el motivo (ej. "se rompio", "merma", "conteo fisico").
6. Toca "Guardar".

## Preguntas frecuentes

**P: Se borraron mis datos / no veo mi información.**

R: Verifica que no dice "MODO DEMO" en la barra amarilla. Si dice MODO DEMO, estás viendo datos de prueba. Si no dice MODO DEMO y no ves tus datos, contacta a tu desarrollador.

**P: Puedo usar el sistema desde otro celular.**

R: Si, siempre que tengas la direccion (URL). Cada persona que entre vera los mismos datos.

**P: Los precios de productos cambian, eso afecta mis cuentas pasadas.**

R: No. El sistema guarda el costo de cada venta al momento en que se hizo. Si el costo sube después, las ventas anteriores no cambian.

**P: Cuanto le debo a cada barbero.**

R: Ve a "Reportes" y luego "Reporte por barbero". Ahi ves el total de comisiones de cada uno en la semana. Los pagos quedan a tu criterio (al final del día o al final de la semana).

**P: Por que "compras" no baja mi ganancia.**

R: Porque comprar mercancia no es perder dinero, es convertirlo en producto. La ganancia baja cuando VENDES ese producto (por el costo de lo vendido). El sistema lo maneja automáticamente. Si tienes dudas, revisa el reporte diario: ahi ves por separado cuanto compraste y cuanto costo lo que vendiste.

**P: Que es "Smoke" y "Ping Pong".**

R: Son conceptos que aparecen en tu cuaderno. Todavia no estan en el sistema. Cuando me expliques que son, los agrego.

## Si algo no funciona

1. Anota lo que estabas haciendo.
2. Toma una foto de la pantalla.
3. Escribe a tu desarrollador con esa información.

**No intentes "arreglarlo" cerrando cosas a la fuerza.** Puede empeorar.

## Respaldos

El sistema guarda los datos en una base de datos. Tu desarrollador puede hacer un respaldo manual si lo necesitas. Hablalo con el para definir cada cuanto tiempo se hace (semanal, mensual, etc.).

Si usas la version en hosting gratuito, el respaldo automático puede no estar configurado. Pregunta a tu desarrollador.