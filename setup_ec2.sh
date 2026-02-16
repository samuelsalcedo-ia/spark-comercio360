#!/bin/bash
# Script de Aprovisionamiento (User Data) para Nodos Spark (Master, Worker, Submit)
# Incluye: Java 17, Python 3, Spark 3.5.1, Git y Drivers (MySQL + AWS S3).

# 1. Actualización e instalación de dependencias básicas
echo "--- INICIANDO ACTUALIZACIÓN DEL SISTEMA ---"
sudo apt-get update
sudo apt-get install -y openjdk-17-jdk python3-pip wget git

# 2. Descarga e Instalación de Spark 3.5.1
echo "--- INSTALANDO SPARK 3.5.1 ---"
cd /opt
sudo wget -q https://archive.apache.org/dist/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz
sudo tar xf spark-3.5.1-bin-hadoop3.tgz
sudo mv spark-3.5.1-bin-hadoop3 spark
sudo rm spark-3.5.1-bin-hadoop3.tgz

# 3. Permisos y Librerías Python
echo "--- CONFIGURANDO PERMISOS Y LIBRERÍAS PYTHON ---"
sudo chown -R ubuntu:ubuntu /opt/spark

# Instalamos pyspark 3.5.1 exacto y librerías de datos útiles
pip3 install pyspark==3.5.1 boto3 pandas numpy pyarrow

# 4. DESCARGA DE DRIVERS (CRÍTICO PARA S3 Y MYSQL)
echo "--- DESCARGANDO DRIVERS (MySQL & AWS) ---"
# Nos movemos a la carpeta de JARs de Spark
cd /opt/spark/jars

# 4.1 Driver MySQL (Versión 8.0.28 - Compatible con MySQL 8)
sudo wget -q https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.28/mysql-connector-java-8.0.28.jar

# 4.2 Drivers AWS S3 (Hadoop AWS + AWS SDK Bundle)
# Versiones compatibles con Hadoop 3.3.4 (que es el que trae Spark 3.5.1)
sudo wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar
sudo wget -q https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar

# 5. Variables de Entorno (Persistencia en .bashrc)
echo "--- CONFIGURANDO VARIABLES DE ENTORNO ---"
echo "export SPARK_HOME=/opt/spark" >> /home/ubuntu/.bashrc
echo "export PATH=\$PATH:/opt/spark/bin:/opt/spark/sbin" >> /home/ubuntu/.bashrc
echo "export PYSPARK_PYTHON=/usr/bin/python3" >> /home/ubuntu/.bashrc
echo "export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64" >> /home/ubuntu/.bashrc

# Aplicar cambios en la sesión actual (por si se usa interactivamente)
source /home/ubuntu/.bashrc

echo "--- ¡APROVISIONAMIENTO COMPLETADO CON ÉXITO! ---"