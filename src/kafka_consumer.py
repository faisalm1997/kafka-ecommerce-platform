from kafka import KafkaConsumer
import json
import boto3
from datetime import datetime
import logging
from data_generator import EcommerceDataGenerator

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_consumer(bootstrap_servers, topic, group_id):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        group_id=group_id,
        auto_offset_reset='earliest',
        session_timeout_ms=45000,
        heartbeat_interval_ms=15000,
        max_poll_interval_ms=600000,
        enable_auto_commit=True,
        auto_commit_interval_ms=5000
    )
    logger.info(f"Connected to Kafka, assigned partitions: {consumer.assignment()}")
    return consumer

def upload_to_s3(data, s3_client, bucket_name, date):
    key = f"ecommerce-orders/{date}.json"
    try:
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=json.dumps(data))
        logger.info(f"Data saved to S3: s3://{bucket_name}/{key}")
    except Exception as e:
        logger.error(f"Failed to save data to S3: {str(e)}", exc_info=True)

def main():
    bootstrap_servers = ['my-kafka-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092']
    topic = 'ecommerce-orders'
    group_id = 'ecommerce-group'
    bucket_name = 'faisalm-real-time-data-platform-logs'
    
    s3_client = boto3.client('s3')
    consumer = create_consumer(bootstrap_servers, topic, group_id)
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    daily_data = []

    try:
        for message in consumer:
            logger.info(f"Received message: {message.value}")
            daily_data.append(message.value)
            
            message_date = datetime.now().strftime('%Y-%m-%d')
            if message_date != current_date:
                upload_to_s3(daily_data, s3_client, bucket_name, current_date)
                daily_data = []
                current_date = message_date

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
    finally:
        if daily_data:
            upload_to_s3(daily_data, s3_client, bucket_name, current_date)
        if consumer:
            consumer.close()
            logger.info("Consumer closed successfully")

if __name__ == "__main__":
    main()