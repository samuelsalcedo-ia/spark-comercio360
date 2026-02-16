# Comercio360: Pipeline Big Data con Apache Spark en AWS

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
* **Infraestructura como Código (IaC):** Bash scripting para aprovisionamiento.
* **Librerías Clave:** `mysql-connector-java`, `hadoop-aws`.
* **DevOps:** Despliegue automatizado mediante Git/GitHub y gestión de secretos con Variables de Entorno.

## 📂 Estructura del Proyecto

* `setup_ec2.sh`: **Script de Aprovisionamiento (IaC)**. Instala Java, Spark, Python, Git y descarga automáticamente los drivers necesarios (MySQL/AWS).
* `job_analytics_completo.py`: **Script Principal ETL**. Realiza la ingesta desde S3, transformaciones (Joins, Window Functions) y carga en RDS.
* `consultar_resultados_sql.py`: Script de auditoría que conecta a RDS y muestra las tablas resultantes por consola para verificar la persistencia.
* `requirements.txt`: Lista de dependencias de Python.
* `README.md`: Documentación oficial del proyecto.

## 📊 Lógica de Negocio (Consultas)

El pipeline resuelve tres necesidades analíticas críticas:

1.  **Consulta A (Top Productos):** Ranking diario de los 10 productos con mayor facturación.
2.  **Consulta B (KPIs Mensuales):** Agregación mensual calculando clientes únicos, ticket medio y total de ventas por categoría.
3.  **Consulta C (Detección de Outliers):** Algoritmo estadístico avanzado usando Ventanas Deslizantes (*Rolling Windows*) para detectar días con ventas anómalas (superiores a la media de los 30 días previos + 2 desviaciones estándar).

## ⚙️ Instalación y Despliegue

### 1. Aprovisionamiento de Infraestructura (User Data)
El proyecto incluye un script de automatización (`setup_ec2.sh`) que prepara el entorno.

Para desplegar un nuevo nodo en AWS EC2:
1.  Lanzar instancia (Ubuntu 22.04).
2.  En la sección **Advanced Details** -> **User Data**, pegar el contenido de `setup_ec2.sh`.
3.  Al iniciar, la máquina tendrá Spark, Git y los Drivers configurados automáticamente.

### 2. Configuración del Clúster (Arranque Manual)
Una vez aprovisionados los nodos, es necesario iniciar los demonios de Spark y conectar los Workers al Master:

**En el Nodo Master:**
```bash
# Iniciar el proceso maestro
/opt/spark/sbin/start-master.sh
# Nota: Copiar la URL del log (ej: spark://ip-172-31-XX-XX:7077)

```

**En cada Nodo Worker (x3):**

```bash
# Conectar el worker al maestro
/opt/spark/sbin/start-worker.sh spark://<IP-PRIVADA-MASTER>:7077

```

### 3. Clonar el Repositorio

En el nodo Submit (Cliente), descargamos el código fuente:

```bash
git clone [https://github.com/samuelsalcedo-ia/spark-comercio360.git](https://github.com/samuelsalcedo-ia/spark-comercio360.git)
cd spark-comercio360

```

### 4. Configuración de Seguridad

Por seguridad, **no** incluimos credenciales en el código. Define la contraseña de la base de datos como variable de entorno antes de ejecutar:

```bash
export DB_PASSWORD='[PASSWORD]'

```

### 5. Ejecución del Pipeline ETL

Lanzamos el trabajo al clúster en modo cliente. Se han ajustado los parámetros de memoria para optimizar el rendimiento en instancias `t2.micro`:

```bash
/opt/spark/bin/spark-submit \
  --master spark://<IP-PRIVADA-MASTER>:7077 \
  --deploy-mode client \
  --executor-memory 512M \
  --driver-memory 512M \
  --conf spark.executor.cores=1 \
  --conf spark.cores.max=3 \
  --driver-class-path /opt/spark/jars/mysql-connector-java-8.0.28.jar \
  --jars /opt/spark/jars/hadoop-aws-3.3.4.jar,/opt/spark/jars/aws-java-sdk-bundle-1.12.262.jar,/opt/spark/jars/mysql-connector-java-8.0.28.jar \
  job_analytics_completo.py

```

### 6. Verificación de Resultados (Auditoría)

Para confirmar que los datos se han guardado correctamente en MySQL, ejecutamos el script de validación que consulta directamente a la base de datos:

```bash
/opt/spark/bin/spark-submit \
  --driver-class-path /opt/spark/jars/mysql-connector-java-8.0.28.jar \
  --jars /opt/spark/jars/mysql-connector-java-8.0.28.jar \
  consultar_resultados_sql.py

```