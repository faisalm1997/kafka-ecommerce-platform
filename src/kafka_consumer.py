from kafka import KafkaConsumer
import json
import boto3
from datetime import datetime
import logging
from config import KAFKA_CONFIG, TOPIC_NAME, S3_BUCKET

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_consumer(group_id):
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=KAFKA_CONFIG['bootstrap.servers'],
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        group_id=group_id,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        auto_commit_interval_ms=5000
    )
    logger.info(f"Connected to Kafka, assigned partitions: {consumer.assignment()}")
    return consumer

def main():
    group_id = 'ecommerce-group'
    consumer = create_consumer(group_id)
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    daily_data = []

    try:
        for message in consumer:
            logger.info(f"Received message: {message.value}")
            daily_data.append(message.value)
            
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
    finally:
        if consumer:
            consumer.close()
            logger.info("Consumer closed successfully")

if __name__ == "__main__":
    main()