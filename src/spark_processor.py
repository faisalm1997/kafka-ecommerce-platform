import json
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EcommerceSparkProcessor:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName(config.spark.app_name) \
            .master(config.spark.master) \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        
    def define_schema(self):
        return StructType([
            StructField("event_id", StringType(), True),
            StructField("event_type", StringType(), True),
            StructField("timestamp", StringType(), True),
            StructField("customer", StructType([
                StructField("id", StringType(), True),
                StructField("name", StringType(), True),
                StructField("email", StringType(), True),
                StructField("city", StringType(), True),
                StructField("country", StringType(), True)
            ]), True),
            StructField("product", StructType([
                StructField("id", StringType(), True),
                StructField("name", StringType(), True),
                StructField("category", StringType(), True),
                StructField("price", DoubleType(), True),
                StructField("brand", StringType(), True)
            ]), True),
            StructField("order", StructType([
                StructField("id", StringType(), True),
                StructField("quantity", IntegerType(), True),
                StructField("total_amount", DoubleType(), True),
                StructField("currency", StringType(), True)
            ]), True)
        ])
    
    def start_processing(self):
        logger.info("Starting Spark streaming processor...")
        
        # Read from Kafka
        kafka_df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", config.kafka.bootstrap_servers) \
            .option("subscribe", config.kafka.topic_name) \
            .option("startingOffsets", "latest") \
            .load()
        
        # Parse JSON data
        schema = self.define_schema()
        parsed_df = kafka_df.select(
            from_json(col("value").cast("string"), schema).alias("data")
        ).select("data.*")
        
        # Add processing timestamp
        processed_df = parsed_df.withColumn("processed_at", current_timestamp())
        
        # Process different event types
        self.process_orders(processed_df)
        self.process_page_views(processed_df)
        self.process_real_time_analytics(processed_df)
        
        # Keep the application running
        self.spark.streams.awaitAnyTermination()
    
    def process_orders(self, df):
        """Process order events"""
        orders_df = df.filter(col("event_type") == "order_placed")
        
        # Calculate running totals by category
        category_totals = orders_df \
            .groupBy(
                window(col("processed_at"), "1 minute"),
                col("product.category")
            ) \
            .agg(
                sum("order.total_amount").alias("total_revenue"),
                count("*").alias("order_count"),
                avg("order.total_amount").alias("avg_order_value")
            )
        
        # Write to console (replace with database in production)
        query = category_totals.writeStream \
            .outputMode("update") \
            .format("console") \
            .option("truncate", False) \
            .trigger(processingTime='30 seconds') \
            .start()
    
    def process_page_views(self, df):
        """Process page view events"""
        page_views_df = df.filter(col("event_type") == "page_view")
        
        # Top viewed products
        top_products = page_views_df \
            .groupBy(
                window(col("processed_at"), "2 minutes"),
                col("product.name"),
                col("product.category")
            ) \
            .count() \
            .orderBy(desc("count"))
        
        query = top_products.writeStream \
            .outputMode("complete") \
            .format("console") \
            .option("truncate", False) \
            .trigger(processingTime='60 seconds') \
            .start()
    
    def process_real_time_analytics(self, df):
        """Generate real-time analytics"""
        # Customer activity by country
        country_activity = df \
            .groupBy(
                window(col("processed_at"), "1 minute"),
                col("customer.country"),
                col("event_type")
            ) \
            .count()
        
        query = country_activity.writeStream \
            .outputMode("update") \
            .format("console") \
            .option("truncate", False) \
            .trigger(processingTime='30 seconds') \
            .start()

if __name__ == "__main__":
    processor = EcommerceSparkProcessor()
    processor.start_processing()