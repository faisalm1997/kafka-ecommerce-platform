from kafka import KafkaProducer
import json
import logging
from data_generator import EcommerceDataGenerator
from config import KAFKA_CONFIG, TOPIC_NAME

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_producer():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_CONFIG['bootstrap.servers'],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    return producer

def main():
    producer = create_producer()
    data_generator = EcommerceDataGenerator()

    try:
        while True:
            event = data_generator.generate_event()
            producer.send(TOPIC_NAME, value=event)
            producer.flush()
            logger.info(f"Sent event: {event}")
    
    except Exception as e:
        logger.error(f"Error producing messages: {str(e)}")
    finally:
        if producer:
            producer.close()
            logger.info("Producer closed successfully")

if __name__ == "__main__":
    main()