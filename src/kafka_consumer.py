from confluent_kafka import Consumer
import json
import logging
import boto3
from datetime import datetime
import tempfile
from config import KAFKA_CONFIG, TOPIC_NAME

S3_BUCKET_NAME = 'confluent-kafka-ecommerce-data'
S3_PREFIX = 'kafka-consumer-logs/'

s3_client = boto3.client("s3")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_to_s3(data, key):
    """Upload data to S3 bucket."""
    try:
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
            json.dump(data, tmp)
            tmp.flush()
            s3_client.upload_file(tmp.name, S3_BUCKET_NAME, key)
        logger.info(f"Data uploaded to S3: {key}")
    except Exception as e:
        logger.error(f"Failed to upload data to S3: {e}")

def create_consumer(group_id):
    conf = {
        'bootstrap.servers': KAFKA_CONFIG['bootstrap.servers'],
        'group.id': group_id,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True
    }
    return Consumer(conf)

def main():
    consumer = create_consumer('ecommerce-group')
    consumer.subscribe([TOPIC_NAME])
    
    batch = []
    batch_size = 100
    
    try:
        while True:
            msg = consumer.poll(1.0)
            
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Consumer error: {msg.error()}")
                continue
                
            try:
                value = json.loads(msg.value().decode('utf-8'))
                logger.info(f"Received order: {value['order_id']}")
                batch.append(value)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                
            if len(batch) >= batch_size:
                key = f"{S3_PREFIX}{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                upload_to_s3(batch, key)
                batch = []
                
    except KeyboardInterrupt:
        logger.info("Stopping consumer...")
    finally:
        consumer.close()
        logger.info("Consumer closed successfully")

    # Upload any remaining messages
    if batch:
        key = f"{S3_PREFIX}{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        upload_to_s3(batch, key)

if __name__ == "__main__":
    main()