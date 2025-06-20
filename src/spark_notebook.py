import pandas as pd
import json
import boto3
import streamlit as st
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import SQLContext

# S3 bucket and other information
s3_client = boto3.client('s3')
s3a_path = "s3a://confluent-kafka-ecommerce-data/kafka-consumer-logs/*"
s3a_output = "s3a://confluent-kafka-ecommerce-data/kafka-consumer-logs_output/"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Start Spark session
spark = SparkSession.builder \
    .appName("ReadDataFromS3") \
    .config("spark.hadoop.fs.s3a.aws.credentials.provider", "com.amazonaws.auth.DefaultAWSCredentialsProviderChain") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.1") \
    .getOrCreate()

SQLContext = SQLContext(spark)

# List all objects in the S3 bucket
file_list = spark.sparkContext.wholeTextFiles(s3a_path).map(lambda x: x[0]).collect()
for file_path in file_list:
    print(file_path)

# Infer schema from pyspark 

# df = spark.read.json("s3a://confluent-kafka-ecommerce-data/kafka-consumer-logs/*.json")
# df.printSchema()
# df.show(truncate=False)

# Schema definition for the JSON data
schema = StructType([
    StructField("currency", StringType(), True),
    StructField("customer", StructType([
        StructField("account_age_days", LongType(), True),
        StructField("country", StringType(), True),
        StructField("customer_id", LongType(), True),
        StructField("email", StringType(), True),
        StructField("is_premium", BooleanType(), True),
    ]), True),
    StructField("order_id", StringType(), True),
    StructField("payment_method", StringType(), True),
    StructField("products", ArrayType(
        StructType([
            StructField("category", StringType(), True),
            StructField("in_stock", BooleanType(), True),
            StructField("name", StringType(), True),
            StructField("price", DoubleType(), True),
            StructField("product_id", LongType(), True),
            StructField("vendor", StringType(), True),
        ])
    ), True),
    StructField("shipping_cost", DoubleType(), True),
    StructField("shipping_method", StringType(), True),
    StructField("status", StringType(), True),
    StructField("subtotal", DoubleType(), True),
    StructField("tax", DoubleType(), True),
    StructField("timestamp", StringType(), True),
    StructField("total_amount", DoubleType(), True),
])

# output = SQLContext.createDataFrame(spark.emptyRDD(), schema)

df_json = spark.read.json(s3a_path, schema=schema)

df_flat = df_json.withColumn("product", explode("products")) \
    .select(
        "*",
        col("customer.account_age_days"),
        col("customer.country"),
        col("customer.customer_id"),
        col("customer.email"),
        col("customer.is_premium"),
        col("product.*")
    ) \
    .drop("customer", "products", "product")

df_flat.show(truncate=False)

# Write flat table to S3 in CSV format 

df_flat_single_output = df_flat.coalesce(1)  # Ensure single output file

df_flat_single_output.write \
    .option("header", True) \
    .option("delimiter", ",") \
    .mode("overwrite") \
    .csv(s3a_output)
