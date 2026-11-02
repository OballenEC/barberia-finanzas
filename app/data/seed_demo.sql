-- SOLO datos ficticios. Idempotente por seed_key / claves únicas.

INSERT OR IGNORE INTO servicios (nombre, precio_sugerido, activo, seed_key) VALUES
  ('Corte',          '100.00', 1, 'demo-svc-corte'),
  ('Barba',          '70.00',  1, 'demo-svc-barba'),
  ('Corte + Barba',  '150.00', 1, 'demo-svc-combo');

INSERT OR IGNORE INTO productos (nombre, codigo_interno, costo_promedio, precio_venta, stock_actual, activo, seed_key) VALUES
  ('Cera para cabello',  'PROD-CERA',   '80.00',  '150.00', 0, 1, 'demo-prod-cera'),
  ('Shampoo barbería',   'PROD-SHAMP',  '60.00',  '120.00', 0, 1, 'demo-prod-shamp'),
  ('Aceite para barba',  'PROD-ACEITE', '90.00',  '180.00', 0, 1, 'demo-prod-aceite');

-- Las operaciones de demo se insertan desde scripts/seed_demo.py para
-- mantener la consistencia del CPM y del libro mayor de inventario.