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

KAFKA_TOPIC = "user-activity-logs"
BATCH_SIZE = 100
S3_BUCKET = "faisalm-real-time-data-platform-logs"

# Kafka local setup
KAFKA_BROKER = "my-kafka-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092"
PRODUCER_TOPIC = os.getenv("PRODUCER_TOPIC", "ecommerce-data")
CONSUMER_TOPIC = os.getenv("CONSUMER_TOPIC", "ecommerce-data")

# AWS Setup
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

KAFKA_CONFIG = {
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'broker:29092'),
    'client.id': 'ecommerce-client',
    'security.protocol': 'PLAINTEXT'
}

SCHEMA_REGISTRY_URL = os.getenv('SCHEMA_REGISTRY_URL', 'http://schema-registry:8081')
TOPIC_NAME = 'ecommerce-orders'