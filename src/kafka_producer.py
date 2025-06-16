from kafka import KafkaProducer
import json
from data_generator import EcommerceDataGenerator
import time
import logging

logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for more visibility
logger = logging.getLogger(__name__)

# Initialize data generator
generator = EcommerceDataGenerator()

producer = KafkaProducer(
    bootstrap_servers=['my-kafka-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

BATCH_SIZE = 100

while True:
    try:
        # Generate batch of orders
        orders = generator.generate_batch(BATCH_SIZE)
        
        # Send each order to Kafka
        for order in orders:
            future = producer.send('ecommerce-orders', order)
            # Wait for message to be sent
            record_metadata = future.get(timeout=10)
            logger.info(f"Sent order {order['order_id']} to partition {record_metadata.partition} at offset {record_metadata.offset}")
        
        producer.flush()
        logger.info(f"Successfully sent batch of {BATCH_SIZE} orders")
        time.sleep(5)
        
    except Exception as e:
        logger.error(f"Error producing messages: {str(e)}", exc_info=True)
        time.sleep(1)