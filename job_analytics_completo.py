import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# --- VARIABLES DE ENTORNO ---
db_password = os.getenv('DB_PASSWORD')
if not db_password:
    print("ERROR CRÍTICO: La variable de entorno 'DB_PASSWORD' no está definida.")
    sys.exit(1)

rds_endpoint = "database-1.cngtn9hm4jjt.us-east-1.rds.amazonaws.com"

# --- INICIO DE SPARK ---
spark = (SparkSession.builder
    .appName("Comercio360 - Analytics Completo (GitHub Version)")
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .config("spark.hadoop.fs.s3a.aws.credentials.provider", "com.amazonaws.auth.InstanceProfileCredentialsProvider")
    .config("spark.jars", "/opt/spark/jars/mysql-connector-java-8.0.28.jar")
    .getOrCreate())

# Configuración de rutas
bucket_name = "comercio360-samuel-salcedo"
base_path = f"s3a://{bucket_name}/comercio360/raw"

print(f"--- 1. LECTURA DE DATOS DESDE S3: {bucket_name} ---")
df_orders = spark.read.csv(f"{base_path}/orders.csv", header=True, inferSchema=True)
df_items = spark.read.csv(f"{base_path}/order_items.csv", header=True, inferSchema=True)
df_products = spark.read.csv(f"{base_path}/products.csv", header=True, inferSchema=True)

# Preprocesamiento: JOIN y Casteo de Fechas
df_joined = df_items.join(df_orders, "order_id").join(df_products, "product_id")
df_ventas = df_joined.withColumn("importe_total", F.col("quantity") * F.col("unit_price")) \
                     .withColumn("order_date", F.to_date("order_date"))

# ==========================================
# CONSULTA A: TOP PRODUCTOS DIARIO
# ==========================================
print("--- Procesando Consulta A: Top Productos... ---")
df_a = df_ventas.groupBy("order_date", "product_id", "product_name") \
    .agg(F.sum("quantity").alias("unidades"), F.sum("importe_total").alias("importe_total"))

w_a = Window.partitionBy("order_date").orderBy(F.desc("importe_total"))
df_final_a = df_a.withColumn("ranking", F.rank().over(w_a)).filter(F.col("ranking") <= 10)

# ==========================================
# CONSULTA B: KPI MENSUAL POR CATEGORIA
# ==========================================
print("--- Procesando Consulta B: KPIs Mensuales... ---")
# Usamos 'product_id' como agrupación simplificada (o 'category_id' si existe)
df_final_b = df_ventas.withColumn("mes", F.date_format("order_date", "yyyy-MM")) \
    .groupBy("mes", "product_id") \
    .agg(
        F.countDistinct("customer_id").alias("clientes_unicos"),,
        F.count("order_id").alias("num_pedidos"),
        F.avg("importe_total").alias("ticket_medio"),
        F.sum("importe_total").alias("total_mensual")
    )

# ==========================================
# CONSULTA C: OUTLIERS (Con Simulación de Tienda)
# ==========================================
print("--- Procesando Consulta C: Outliers... ---")
# Simulación: Asignamos aleatoriamente una tienda (1-5) a cada venta
df_ventas_store = df_ventas.withColumn("store_id", (F.rand() * 5).cast("int") + 1)

# 1. Agrupar por tienda y día
df_c_daily = df_ventas_store.groupBy("store_id", "order_date") \
    .agg(F.sum("importe_total").alias("ventas_dia"))

# 2. Ventana de 30 días previos
w_c = Window.partitionBy("store_id").orderBy("order_date").rowsBetween(-30, -1)

# 3. Estadísticas y Flag
df_final_c = df_c_daily \
    .withColumn("media_30d", F.avg("ventas_dia").over(w_c)) \
    .withColumn("desviacion_30d", F.stddev("ventas_dia").over(w_c)) \
    .withColumn("is_outlier", 
                F.when(F.col("ventas_dia") > (F.col("media_30d") + 2 * F.col("desviacion_30d")), "SI")
                .otherwise("NO")) \
    .na.fill(0)

# ==========================================
# ESCRITURA EN RDS (MYSQL)
# ==========================================
print(f"--- Conectando a MySQL: {rds_endpoint} ---")
jdbc_url = f"jdbc:mysql://{rds_endpoint}:3306/comercio360?useSSL=false"
props = {"user": "admin", "password": db_password, "driver": "com.mysql.cj.jdbc.Driver"}

tablas = [
    (df_final_a, "consulta_a_top_productos"),
    (df_final_b, "consulta_b_kpis_mensuales"),
    (df_final_c, "consulta_c_outliers")
]

for df, tabla in tablas:
    print(f"Volcando tabla: {tabla}...")
    df.write.jdbc(jdbc_url, tabla, mode="overwrite", properties=props)

print("--- ¡ÉXITO! Pipeline Analytics completado ---")
spark.stop()
