from confluent_kafka import Consumer
import json
import logging
from datetime import datetime
from config import KAFKA_CONFIG, TOPIC_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                
    except KeyboardInterrupt:
        logger.info("Stopping consumer...")
    finally:
        consumer.close()
        logger.info("Consumer closed successfully")

if __name__ == "__main__":
    main()