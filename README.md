# 🛒 Comercio360: Pipeline Big Data con Apache Spark en AWS

Este proyecto implementa una arquitectura de procesamiento de datos distribuida y escalable utilizando **Apache Spark** sobre infraestructura **AWS EC2**. El objetivo es procesar históricos de ventas (ETL), calcular métricas de negocio complejas y persistir los resultados en una base de datos **RDS MySQL**.

## 🚀 Arquitectura del Clúster

El despliegue se ha realizado en AWS siguiendo las mejores prácticas de separación de roles y seguridad:

* **Infraestructura de Cómputo (EC2):**
    * **Master Node:** `t2.medium` (Orquestador del clúster).
    * **Worker Nodes (x3):** `t2.micro` (Procesamiento distribuido).
    * **Submit Node:** `t2.micro` (Cliente/Bastión para lanzamiento de jobs).
* **Almacenamiento:**
    * **Data Lake:** Amazon S3 (Datos crudos CSV).
    * **Base de Datos Operacional:** Amazon RDS (MySQL 8.0) para la capa de servicio.

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3 (PySpark).
* **Motor:** Apache Spark 3.5.1.
* **Base de Datos:** MySQL 8.0 (AWS RDS).
* **Librerías Clave:** `mysql-connector-java`, `hadoop-aws`.
* **DevOps:** Despliegue automatizado mediante Git/GitHub y gestión de secretos con Variables de Entorno.

## 📂 Estructura del Proyecto

* `job_analytics_completo.py`: **Script Principal ETL**. Realiza la ingesta desde S3, transformaciones (Joins, Window Functions) y carga en RDS.
* `consultar_resultados_sql.py`: Script de verificación que conecta a RDS y muestra las tablas resultantes por consola.
* `README.md`: Documentación del proyecto.

## 📊 Lógica de Negocio (Consultas)

El pipeline resuelve tres necesidades analíticas críticas:

1.  **Consulta A (Top Productos):** Ranking diario de los 10 productos con mayor facturación.
2.  **Consulta B (KPIs Mensuales):** Agregación mensual calculando clientes únicos, ticket medio y total de ventas por categoría.
3.  **Consulta C (Detección de Outliers):** Algoritmo estadístico avanzado usando Ventanas Deslizantes (*Rolling Windows*) para detectar días con ventas anómalas (superiores a la media de los 30 días previos + 2 desviaciones estándar).

## ⚙️ Instalación y Despliegue

### 1. Prerrequisitos
* Tener acceso al clúster Spark en AWS.
* Tener las librerías de conexión (`mysql-connector-java` y `hadoop-aws`) en `/opt/spark/jars`.

### 2. Clonar el Repositorio
En el nodo Submit (Cliente):
```bash
git clone [https://github.com/samuelsalcedo-ia/spark-comercio360.git](https://github.com/samuelsalcedo-ia/spark-comercio360.git)
cd spark-comercio360
