import os
from dotenv import load_dotenv

load_dotenv()

EVENT_TYPES = {
    "page_view": 0.4,
    "click": 0.3,
    "add_to_cart": 0.2,
    "purchase": 0.1
}

PRODUCT_CATEGORIES = [
    "electronics", "clothing", "books", "home"
]

# Kafka Configuration
KAFKA_CONFIG = {
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
    'client.id': 'ecommerce-client',
    'security.protocol': 'PLAINTEXT'
}

# If running in Docker, override the bootstrap servers
if os.getenv('DOCKER_ENV'):
    KAFKA_CONFIG['bootstrap.servers'] = 'broker:29092'

# Topics
TOPIC_NAME = 'ecommerce-events'
BATCH_SIZE = 100