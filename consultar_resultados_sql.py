import os
from pyspark.sql import SparkSession

# Lectura de credenciales
db_password = os.getenv('DB_PASSWORD')
rds_endpoint = "database-1.cngtn9hm4jjt.us-east-1.rds.amazonaws.com"
# Importante: Añadimos allowPublicKeyRetrieval=true también aquí
jdbc_url = f"jdbc:mysql://{rds_endpoint}:3306/comercio360?useSSL=false&allowPublicKeyRetrieval=true"

spark = (SparkSession.builder
    .appName("Verificación Final RDS")
    .config("spark.jars", "/opt/spark/jars/mysql-connector-java-8.0.28.jar")
    .getOrCreate())

def mostrar_tabla(nombre_tabla):
    print(f"\n>>> VERIFICANDO TABLA: {nombre_tabla} <<<")
    df = spark.read \
        .format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", nombre_tabla) \
        .option("user", "admin") \
        .option("password", db_password) \
        .option("driver", "com.mysql.cj.jdbc.Driver") \
        .load()
    
    df.show(5, truncate=False)

# Mostrar las 3 tablas
mostrar_tabla("consulta_a_top_productos")
mostrar_tabla("consulta_b_kpis_mensuales")
mostrar_tabla("consulta_c_outliers")

spark.stop()
