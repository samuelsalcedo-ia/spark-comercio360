-- Script de inicialización de Base de Datos Comercio360
-- Este script define la estructura de las tablas de resultados.
-- Ejecutar en MySQL Workbench o CLI si se despliega el proyecto desde cero.

CREATE DATABASE IF NOT EXISTS comercio360;
USE comercio360;

-- -----------------------------------------------------
-- TABLA 1: Ranking de Productos (Consulta A)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS consulta_a_top_productos (
    order_date DATE,
    product_id INT,
    product_name VARCHAR(255),
    unidades INT,
    importe_total DECIMAL(15,2),
    ranking INT
);

-- -----------------------------------------------------
-- TABLA 2: KPIs Mensuales (Consulta B)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS consulta_b_kpis_mensuales (
    mes VARCHAR(10), -- Formato YYYY-MM
    category_id INT,
    clientes_unicos INT,
    num_pedidos INT,
    ticket_medio DECIMAL(15,2),
    facturacion_mensual DECIMAL(15,2)
);

-- -----------------------------------------------------
-- TABLA 3: Detección de Outliers (Consulta C)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS consulta_c_outliers (
    store_id INT,
    order_date DATE,
    ventas_dia DECIMAL(15,2),
    media_30d DECIMAL(15,2),
    desviacion_30d DECIMAL(15,2),
    is_outlier VARCHAR(5) -- Valores: 'YES' o 'NO'
);