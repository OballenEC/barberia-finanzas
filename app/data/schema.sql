-- Dinero como TEXT con formato "1234.50" (Decimal-as-TEXT).
-- Estados: 'valida' | 'anulada'
-- seed_key: NULL para datos reales; string estable para datos demo.

CREATE TABLE IF NOT EXISTS servicios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    precio_sugerido TEXT NOT NULL CHECK (precio_sugerido GLOB '*[0-9]*'),
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    seed_key TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS barberos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    comision_pct_default TEXT NOT NULL DEFAULT '35.00',
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    seed_key TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS ventas_servicio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    servicio_id INTEGER NOT NULL REFERENCES servicios(id),
    barbero_id INTEGER REFERENCES barberos(id),
    fecha_hora TEXT NOT NULL,
    precio_cobrado TEXT NOT NULL,
    metodo_pago TEXT NOT NULL DEFAULT 'efectivo',
    comision_pct TEXT,
    comision_monto TEXT,
    estado TEXT NOT NULL DEFAULT 'valida' CHECK (estado IN ('valida','anulada')),
    anulada_por_id INTEGER REFERENCES ventas_servicio(id),
    motivo_anulacion TEXT,
    creado_en TEXT NOT NULL,
    seed_key TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS gastos_operativos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    categoria TEXT NOT NULL,
    importe TEXT NOT NULL,
    metodo_pago TEXT NOT NULL DEFAULT 'efectivo',
    estado TEXT NOT NULL DEFAULT 'valida' CHECK (estado IN ('valida','anulada')),
    motivo_anulacion TEXT,
    creado_en TEXT NOT NULL,
    seed_key TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    codigo_interno TEXT UNIQUE,
    costo_promedio TEXT NOT NULL DEFAULT '0.00',
    precio_venta TEXT NOT NULL DEFAULT '0.00',
    stock_actual INTEGER NOT NULL DEFAULT 0 CHECK (stock_actual >= 0),
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    seed_key TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS compras_inventario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    costo_unitario TEXT NOT NULL,
    total TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'valida' CHECK (estado IN ('valida','anulada')),
    motivo_anulacion TEXT,
    creado_en TEXT NOT NULL,
    seed_key TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS ventas_producto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    barbero_id INTEGER REFERENCES barberos(id),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario TEXT NOT NULL,
    total_venta TEXT NOT NULL,
    costo_unitario_snapshot TEXT NOT NULL,
    costo_total_snapshot TEXT NOT NULL,
    comision_pct TEXT,
    comision_monto TEXT,
    estado TEXT NOT NULL DEFAULT 'valida' CHECK (estado IN ('valida','anulada')),
    motivo_anulacion TEXT,
    creado_en TEXT NOT NULL,
    seed_key TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS movimientos_inventario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    tipo TEXT NOT NULL CHECK (tipo IN (
        'compra','venta','ajuste_positivo','ajuste_negativo',
        'anulacion_compra','anulacion_venta'
    )),
    cantidad INTEGER NOT NULL,
    costo_unitario TEXT NOT NULL,
    referencia_tipo TEXT NOT NULL,
    referencia_id INTEGER NOT NULL,
    motivo TEXT,
    creado_en TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ajustes_inventario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    cantidad_delta INTEGER NOT NULL CHECK (cantidad_delta <> 0),
    motivo TEXT NOT NULL,
    usuario TEXT,
    creado_en TEXT NOT NULL,
    seed_key TEXT UNIQUE
);

CREATE INDEX IF NOT EXISTS idx_ventas_servicio_fecha ON ventas_servicio(fecha_hora);
CREATE INDEX IF NOT EXISTS idx_ventas_servicio_barbero ON ventas_servicio(barbero_id);
CREATE INDEX IF NOT EXISTS idx_gastos_fecha ON gastos_operativos(fecha);
CREATE INDEX IF NOT EXISTS idx_compras_fecha ON compras_inventario(fecha);
CREATE INDEX IF NOT EXISTS idx_ventas_producto_fecha ON ventas_producto(fecha);
CREATE INDEX IF NOT EXISTS idx_ventas_producto_barbero ON ventas_producto(barbero_id);
CREATE INDEX IF NOT EXISTS idx_movimientos_producto ON movimientos_inventario(producto_id, fecha);