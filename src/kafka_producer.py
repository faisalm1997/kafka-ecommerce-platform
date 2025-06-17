from confluent_kafka import Producer
import json
import logging
import time
from data_generator import EcommerceDataGenerator
from config import KAFKA_CONFIG, TOPIC_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def delivery_report(err, msg):
    if err is not None:
        logger.error(f'Message delivery failed: {err}')
    else:
        logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def create_producer():
    conf = {
        'bootstrap.servers': KAFKA_CONFIG['bootstrap.servers'],
        'client.id': KAFKA_CONFIG['client.id']
    }
    return Producer(conf)

def main():
    producer = create_producer()
    data_generator = EcommerceDataGenerator()

    try:
        while True:
            order = data_generator.generate_order()
            producer.produce(
                TOPIC_NAME,
                key=str(order['order_id']),
                value=json.dumps(order),
                callback=delivery_report
            )
            producer.poll(0)
            time.sleep(1)  # Add delay between messages
            
    except KeyboardInterrupt:
        logger.info("Stopping producer...")
    except Exception as e:
        logger.error(f"Error producing messages: {str(e)}")
    finally:
        logger.info("Flushing producer...")
        producer.flush(timeout=10)
        logger.info("Producer closed successfully")

if __name__ == "__main__":
    main()