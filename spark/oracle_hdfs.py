from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType

def process_table(spark, table_name, hdfs_path, oracle_url, oracle_user, oracle_password, cast_columns=None):
    df = spark.read \
        .format("jdbc") \
        .option("url", oracle_url) \
        .option("dbtable", table_name) \
        .option("user", oracle_user) \
        .option("password", oracle_password) \
        .load()

    if cast_columns:
        for column, data_type in cast_columns.items():
            df = df.withColumn(column, df[column].cast(data_type))

    print(f"Processing table: {table_name}")
    df.printSchema()
    df.show()

    df.write.format("parquet").mode("overwrite").save(hdfs_path)

if __name__ == "__main__":
    spark = SparkSession.builder.appName("Oracle to HDFS").master("spark://spark-master:7077").getOrCreate()

    oracle_url = "jdbc:oracle:thin:@oracle:1521:ORCLCDB"
    oracle_user = "sys as sysdba"
    oracle_password = "pass"

    tables = [
        {
            "table_name": "customer",
            "hdfs_path": "hdfs://hadoop-namenode:8020/user/spark/extracts/customer",
            "cast_columns": {"customer_id": IntegerType()}
        },
        {
            "table_name": "address",
            "hdfs_path": "hdfs://hadoop-namenode:8020/user/spark/extracts/address",
            "cast_columns": {"address_id": IntegerType()}
        },
        {
            "table_name": "customer_address_join",
            "hdfs_path": "hdfs://hadoop-namenode:8020/user/spark/extracts/customer_address_join",
            "cast_columns": {
                "customer_id": IntegerType(),
                "address_id": IntegerType()
            }
        }
    ]

    for table in tables:
        process_table(
            spark=spark,
            table_name=table["table_name"],
            hdfs_path=table["hdfs_path"],
            oracle_url=oracle_url,
            oracle_user=oracle_user,
            oracle_password=oracle_password,
            cast_columns=table.get("cast_columns")
        )

    spark.stop()
