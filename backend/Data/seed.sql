-- =============================================
-- RAG Demo — Grupo Altamira S.A.
-- Datos ficticios para demo de RAG
-- =============================================

DROP TABLE IF EXISTS ventas CASCADE;
DROP TABLE IF EXISTS facturas CASCADE;
DROP TABLE IF EXISTS productos CASCADE;
DROP TABLE IF EXISTS clientes CASCADE;

CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    segmento VARCHAR(50),
    pais VARCHAR(50) DEFAULT 'Panamá',
    limite_credito DECIMAL(12,2),
    created_at DATE DEFAULT CURRENT_DATE
);

CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(50),
    precio DECIMAL(10,2),
    costo DECIMAL(10,2),
    margen DECIMAL(5,2)
);

CREATE TABLE facturas (
    id SERIAL PRIMARY KEY,
    cliente_id INT REFERENCES clientes(id),
    monto DECIMAL(12,2),
    fecha DATE,
    fecha_vencimiento DATE,
    estado VARCHAR(20),
    dias_vencida INT DEFAULT 0
);

CREATE TABLE ventas (
    id SERIAL PRIMARY KEY,
    producto_id INT REFERENCES productos(id),
    cliente_id INT REFERENCES clientes(id),
    cantidad INT,
    precio_unitario DECIMAL(10,2),
    fecha DATE
);

-- CLIENTES (15 empresas panameñas ficticias)
INSERT INTO clientes (nombre, segmento, pais, limite_credito) VALUES
('Grupo Torre Alta S.A.',      'Corporativo', 'Panamá',      500000),
('Constructora Pacífico',      'Corporativo', 'Panamá',      350000),
('Farmacia San Judas',         'PYME',        'Panamá',       50000),
('Distribuidora El Volcán',    'PYME',        'Panamá',       80000),
('Hotel Miramar',              'Corporativo', 'Panamá',      200000),
('Supermercados Riba Smith',   'Corporativo', 'Panamá',      450000),
('Clínica Santa Fe',           'PYME',        'Panamá',      120000),
('Tecnología Avanzada S.A.',   'Corporativo', 'Panamá',      300000),
('Importadora Los Andes',      'PYME',        'Colombia',     90000),
('Servicios Globales CR',      'PYME',        'Costa Rica',   70000),
('Banco Regional S.A.',        'Corporativo', 'Panamá',      800000),
('Seguros del Istmo',          'Corporativo', 'Panamá',      600000),
('Restaurantes La Plaza',      'PYME',        'Panamá',       40000),
('Logística Ágil S.A.',        'PYME',        'Panamá',      110000),
('Editorial Centroamérica',    'PYME',        'Panamá',       30000);

-- PRODUCTOS (10 productos con márgenes variados)
INSERT INTO productos (nombre, categoria, precio, costo, margen) VALUES
('Software ERP Básico',        'Software',  4500.00,  900.00, 80.00),
('Software ERP Empresarial',   'Software', 12000.00, 2400.00, 80.00),
('Consultoría Implementación', 'Servicios', 8000.00, 3200.00, 60.00),
('Soporte Anual Premium',      'Servicios', 3600.00,  720.00, 80.00),
('Soporte Anual Básico',       'Servicios', 1200.00,  360.00, 70.00),
('Hardware Servidor Dell',     'Hardware',  6500.00, 5200.00, 20.00),
('Licencias Microsoft 365',    'Software',   180.00,  120.00, 33.00),
('Capacitación Usuarios',      'Servicios', 2500.00,  800.00, 68.00),
('Módulo RRHH Add-on',         'Software',  2200.00,  440.00, 80.00),
('Módulo Inventario Add-on',   'Software',  1800.00,  360.00, 80.00);

-- FACTURAS (20 facturas con estados variados — las vencidas son las más interesantes)
INSERT INTO facturas (cliente_id, monto, fecha, fecha_vencimiento, estado, dias_vencida) VALUES
(1,  12000.00, '2023-10-01', '2023-11-01', 'pagada',   0),
(1,   3600.00, '2023-11-15', '2023-12-15', 'vencida',  62),
(2,   8000.00, '2023-09-01', '2023-10-01', 'pagada',    0),
(2,   6500.00, '2023-12-01', '2024-01-01', 'vencida',  46),
(3,   1200.00, '2023-11-01', '2023-12-01', 'pendiente', 0),
(4,   4500.00, '2023-10-15', '2023-11-15', 'vencida',  62),
(4,   2200.00, '2023-12-15', '2024-01-15', 'pendiente', 0),
(5,  12000.00, '2023-08-01', '2023-09-01', 'pagada',    0),
(5,   3600.00, '2023-12-01', '2024-01-01', 'vencida',  46),
(6,   8000.00, '2023-11-01', '2023-12-01', 'pagada',    0),
(6,   1800.00, '2024-01-05', '2024-02-05', 'pendiente', 0),
(7,   4500.00, '2023-10-01', '2023-11-01', 'vencida',  92),
(8,  12000.00, '2023-12-01', '2024-01-01', 'pendiente', 0),
(9,   2500.00, '2023-11-15', '2023-12-15', 'vencida',  47),
(10,  1200.00, '2024-01-10', '2024-02-10', 'pendiente', 0),
(11, 12000.00, '2023-09-01', '2023-10-01', 'pagada',    0),
(11,  8000.00, '2023-12-01', '2024-01-01', 'pagada',    0),
(12,  3600.00, '2023-11-01', '2023-12-01', 'vencida',  77),
(13,  1200.00, '2023-10-01', '2023-11-01', 'vencida',  91),
(14,  4500.00, '2024-01-01', '2024-02-01', 'pendiente', 0);

-- VENTAS (25 registros)
INSERT INTO ventas (producto_id, cliente_id, cantidad, precio_unitario, fecha) VALUES
(2,  1,   1, 12000.00, '2023-10-01'),
(4,  1,   1,  3600.00, '2023-11-15'),
(3,  2,   1,  8000.00, '2023-09-01'),
(6,  2,   1,  6500.00, '2023-12-01'),
(5,  3,   1,  1200.00, '2023-11-01'),
(1,  4,   1,  4500.00, '2023-10-15'),
(9,  4,   1,  2200.00, '2023-12-15'),
(2,  5,   1, 12000.00, '2023-08-01'),
(4,  5,   1,  3600.00, '2023-12-01'),
(3,  6,   1,  8000.00, '2023-11-01'),
(10, 6,   1,  1800.00, '2024-01-05'),
(1,  7,   1,  4500.00, '2023-10-01'),
(2,  8,   1, 12000.00, '2023-12-01'),
(8,  9,   1,  2500.00, '2023-11-15'),
(5,  10,  1,  1200.00, '2024-01-10'),
(2,  11,  1, 12000.00, '2023-09-01'),
(3,  11,  1,  8000.00, '2023-12-01'),
(4,  12,  1,  3600.00, '2023-11-01'),
(5,  13,  1,  1200.00, '2023-10-01'),
(1,  14,  1,  4500.00, '2024-01-01'),
(7,  1,  25,   180.00, '2023-10-01'),
(7,  5,  50,   180.00, '2023-08-01'),
(7,  11,100,   180.00, '2023-09-01'),
(8,  2,   1,  2500.00, '2023-09-15'),
(8,  6,   1,  2500.00, '2023-11-20');

-- Verificación rápida
SELECT 'clientes' AS tabla, COUNT(*) AS total FROM clientes
UNION ALL SELECT 'productos', COUNT(*) FROM productos
UNION ALL SELECT 'facturas', COUNT(*) FROM facturas
UNION ALL SELECT 'ventas', COUNT(*) FROM ventas;