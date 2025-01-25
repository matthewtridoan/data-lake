from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, from_json
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType

spark = SparkSession.builder \
    .appName("Explode Purchase Order") \
    .master("spark://spark-master:7077") \
    .config("spark.cassandra.connection.host", "cassandra-db") \
    .config("spark.cassandra.connection.port", "9042") \
    .getOrCreate()

data_schema = StructType([
    StructField("customer_id", StringType()),
    StructField("address_id", StringType()),
    StructField("product_ids", ArrayType(StringType()))
])

purchase_order_raw = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .option("keyspace", "my_keyspace") \
    .option("table", "purchase_order") \
    .load()

purchase_order_exploded = purchase_order_raw \
    .select(
        col("order_id"),
        from_json(col("data"), data_schema).alias("parsed_data")
    ) \
    .select(
        col("order_id"),
        col("parsed_data.customer_id").cast("int").alias("customer_id"),
        col("parsed_data.address_id").cast("int").alias("address_id"),
        explode(col("parsed_data.product_ids")).alias("product_id")
    )

purchase_order_exploded.show(truncate=False)

purchase_order_exploded.write \
    .format("parquet") \
    .mode("overwrite") \
    .save("hdfs://hadoop-namenode:8020/user/spark/extracts/purchase_order")
