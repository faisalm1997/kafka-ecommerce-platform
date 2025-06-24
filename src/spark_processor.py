import sys
import re
import logging
from datetime import datetime
import boto3
import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode
from pyspark.sql.types import *

def get_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s"
    )
    return logging.getLogger("SparkProcessor")

def get_schema():
    return StructType([
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

def create_spark_session():
    return SparkSession.builder \
        .appName("KafkaEcommerceSparkProcessor") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "com.amazonaws.auth.DefaultAWSCredentialsProviderChain") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.1") \
        .getOrCreate()

def read_data(spark, schema, input_path):
    return spark.read.schema(schema).json(input_path)

def flatten_and_explode(df):
    return df.withColumn("product", explode("products")) \
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

def write_single_csv_to_s3(df, bucket, output_folder, timestamp, logger):
    tmp_dir = f"s3a://{bucket}/{output_folder}/output_tmp_{timestamp}/"
    final_key = f"{output_folder}/output_{timestamp}.csv"
    prefix = f"{output_folder}/output_tmp_{timestamp}/"

    logger.info(f"Writing DataFrame to temporary S3 directory: {tmp_dir}")
    df.coalesce(1).write.option("header", True).mode("overwrite").csv(tmp_dir)

    s3 = boto3.client("s3")
    logger.info(f"Searching for part file in: {prefix}")
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    part_file_found = False
    for obj in response.get("Contents", []):
        key = obj["Key"]
        if re.match(rf"{prefix}part-.*\.csv", key):
            logger.info(f"Copying {key} to {final_key}")
            s3.copy_object(
                Bucket=bucket,
                CopySource={"Bucket": bucket, "Key": key},
                Key=final_key
            )
            s3.delete_object(Bucket=bucket, Key=key)
            part_file_found = True

    # Clean up all temp files in the temp directory
    logger.info(f"Cleaning up temporary files in {prefix}")
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    for obj in response.get("Contents", []):
        s3.delete_object(Bucket=bucket, Key=obj["Key"])

    if part_file_found:
        logger.info(f"Data written to: s3://{bucket}/{final_key}")
    else:
        logger.warning("No part file found to copy as final output.")

    return f"s3://{bucket}/{final_key}"

def main(
    bucket="confluent-kafka-ecommerce-data",
    input_prefix="kafka-consumer-logs",
    output_folder="kafka-consumer-logs-output"
):
    logger = get_logger()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_path = f"s3a://{bucket}/{input_prefix}/*.json"

    logger.info("Starting Spark session")
    spark = create_spark_session()

    logger.info(f"Reading data from: {input_path}")
    schema = get_schema()
    df = read_data(spark, schema, input_path)

    logger.info("Flattening and exploding DataFrame")
    df_flat = flatten_and_explode(df)

    logger.info("Writing single CSV to S3")
    output_uri = write_single_csv_to_s3(df_flat, bucket, output_folder, timestamp, logger)

    logger.info(f"Processing complete. Output at: {output_uri}")
    spark.stop()

if __name__ == "__main__":
    # Adding command line argument parsing for use
    parser = argparse.ArgumentParser(description="Kafka Ecommerce Spark Processor")
    parser.add_argument("--bucket", type=str, default="confluent-kafka-ecommerce-data")
    parser.add_argument("--input-prefix", type=str, default="kafka-consumer-logs")
    parser.add_argument("--output-folder", type=str, default="kafka-consumer-logs-output")
    args = parser.parse_args()
    main(
        bucket=args.bucket,
        input_prefix=args.input_prefix,
        output_folder=args.output_folder
    )