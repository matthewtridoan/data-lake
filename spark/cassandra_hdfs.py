from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

spark = SparkSession.builder \
    .appName("Product Data Integration") \
    .master("spark://spark-master:7077") \
    .config("spark.cassandra.connection.host", "cassandra-db") \
    .config("spark.cassandra.connection.port", "9042") \
    .getOrCreate()

product_schema = StructType([
    StructField("name", StringType()),
    StructField("price", DoubleType()),
    StructField("brand", StringType())
])

product_raw = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .option("keyspace", "my_keyspace") \
    .option("table", "product") \
    .load()

product_exploded = product_raw \
    .select(
        col("product_id"),
        from_json(col("data"), product_schema).alias("parsed_data")
    ) \
    .select(
        col("product_id"),
        col("parsed_data.name").alias("name"),
        col("parsed_data.price").alias("price"),
        col("parsed_data.brand").alias("brand")
    )

product_exploded.show(truncate=False)

product_exploded.write \
    .format("parquet") \
    .mode("overwrite") \
    .save("hdfs://hadoop-namenode:8020/user/spark/extracts/product")
