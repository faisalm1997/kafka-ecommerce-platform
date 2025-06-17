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
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'broker:29092'),
    'client.id': 'ecommerce-client',
    'security.protocol': 'PLAINTEXT'
}

# Schema Registry Configuration
SCHEMA_REGISTRY_URL = os.getenv('SCHEMA_REGISTRY_URL', 'http://schema-registry:8081')

# Topics
TOPIC_NAME = 'ecommerce-orders'
BATCH_SIZE = 100

# AWS Setup (if still needed)
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = "faisalm-real-time-data-platform-logs"