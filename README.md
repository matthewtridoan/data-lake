# Data Processing and Analysis Project

This project demonstrates a complete data pipeline for integrating Oracle and Cassandra databases, processing data using Apache Spark, storing it in HDFS, and analyzing it with Hive, Trino, and Tableau.

---

## **Starting the Project**

1. Clone the repository:

   ```bash
   git clone https://github.com/matthewtridoan/data-lake.git
   cd data-lake
   ```

2. Start the services with Docker Compose:
   ```bash
   docker-compose up -d
   ```

---

## **Connecting to Oracle Database**

1. Access the Oracle database container:

   ```bash
   docker exec -it oracle-db bash
   ```

2. Start `sqlplus` as `SYSDBA`:

   ```bash
   sqlplus / as sysdba
   ```

3. Default password: `pass`

### **Example Tables**

Run the following SQL commands in `sqlplus` to set up example tables:

```sql
CREATE TABLE customer (
    customer_id INT PRIMARY KEY,
    name VARCHAR2(100)
);

CREATE TABLE address (
    address_id INT PRIMARY KEY,
    address VARCHAR2(255)
);

CREATE TABLE customer_address_join (
    customer_id INT,
    address_id INT,
    PRIMARY KEY (customer_id, address_id),
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY (address_id) REFERENCES address(address_id)
);

INSERT INTO customer (customer_id, name) VALUES (1, 'Alice Smith');
INSERT INTO customer (customer_id, name) VALUES (2, 'Bob Johnson');
INSERT INTO customer (customer_id, name) VALUES (3, 'Carol Williams');

INSERT INTO address (address_id, address) VALUES (1, '123 Elm Street, Springfield');
INSERT INTO address (address_id, address) VALUES (2, '456 Oak Avenue, Metropolis');
INSERT INTO address (address_id, address) VALUES (3, '789 Pine Lane, Gotham');

INSERT INTO customer_address_join (customer_id, address_id) VALUES (1, 1);
INSERT INTO customer_address_join (customer_id, address_id) VALUES (1, 2);
INSERT INTO customer_address_join (customer_id, address_id) VALUES (2, 3);
```

---

## **Connecting to Cassandra**

1. Access the Cassandra database container:

   ```bash
   docker exec -it cassandra-db cqlsh
   ```

2. Set up the tables with the following CQL commands:

```cql
CREATE TABLE product (
    product_id UUID PRIMARY KEY,
    data TEXT
);

CREATE TABLE orders (
    order_id UUID PRIMARY KEY,
    data TEXT
);

INSERT INTO product (product_id, data) VALUES (uuid(), '{"name": "Laptop", "price": 999.99, "brand": "TechCorp"}');
INSERT INTO product (product_id, data) VALUES (uuid(), '{"name": "Smartphone", "price": 799.99, "brand": "MobileInc"}');
INSERT INTO product (product_id, data) VALUES (uuid(), '{"name": "Tablet", "price": 499.99, "brand": "TabCo"}');

-- Generate orders with corresponding product UUIDs
INSERT INTO orders (order_id, data) VALUES (uuid(), '{"customer_id": 1, "address_id": 1, "product_ids": ["product-uuid-1", "product-uuid-2"]}');
```

---

## **Processing Data with Spark**

You can run the Spark jobs to extract and transform the data from Oracle and Cassandra, and store the results in HDFS as Parquet files.

1. Run the Oracle extraction job:

   ```bash
   spark-submit --jars /opt/spark/jars/ojdbc8.jar /opt/spark/oracle_hdfs.py
   ```

2. Run the Cassandra product extraction job:

   ```bash
   spark-submit --jars /opt/spark/jars/spark-cassandra-connector_2.12-3.5.0.jar,/opt/spark/jars/spark-cassandra-connector-assembly_2.12-3.5.1.jar /opt/spark/cassandra_hdfs.py
   ```

3. Run the Cassandra orders extraction and explosion job:
   ```bash
   spark-submit --jars /opt/spark/jars/spark-cassandra-connector_2.12-3.5.0.jar,/opt/spark/jars/spark-cassandra-connector-assembly_2.12-3.5.1.jar /opt/spark/cassandra_explode_hdfs.py
   ```

---

## **Creating Hive External Tables**

1. Access the Hive container:

   ```bash
   docker exec -it hive bash
   ```

2. Open the Hive CLI:

   ```bash
   beeline -u jdbc:hive2://hive:10000
   ```

3. Create external tables pointing to the Parquet files in HDFS. For example:
   ```sql
   CREATE EXTERNAL TABLE IF NOT EXISTS purchase_order (
       order_id STRING,
       customer_id INT,
       address_id INT,
       product_id STRING
   )
   STORED AS PARQUET
   LOCATION 'hdfs://hadoop-namenode:8020/user/spark/extracts/purchase_order';
   ```

---

## **Querying with Trino**

1. Access Trino CLI or UI:

   ```bash
   docker exec -it trino trino
   ```

2. Show available schemas:

   ```sql
   SHOW SCHEMAS FROM hive;
   ```

3. Use the default schema:

   ```sql
   USE hive.default;
   ```

4. Run queries:
   ```sql
   SELECT * FROM purchase_order LIMIT 10;
   ```

---

## **Visualizing in Tableau**

1. Download the Trino JDBC driver: [Trino JDBC Driver](https://trino.io/docs/current/client/jdbc.html)

2. Open Tableau and choose **JDBC Connection**.

3. Use the following connection details:

   - **URL**: `jdbc:trino:localhost:8080/hive/default`
   - **Driver Class Name**: `io.trino.jdbc.TrinoDriver`

4. Visualize the data by dragging tables and fields into the workspace.
