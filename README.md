# Kafka Ecommerce Analytics Platform

A comprehensive real-time ecommerce analytics platform built with Confluent Kafka, running locally with Docker Compose and visualising data using streamlit.

## Architecture

- **Confluent Kafka**: Message streaming platform
- **Producer**: Generates mock ecommerce events
- **Consumer**: Processes individual events
- **Spark Processor**: Real-time stream processing and analytics
- **Dashboard**: Streamlit-based real-time visualization
- **Control Center**: Confluent's management interface

## Features

- Real-time ecommerce event generation (orders, page views, cart actions)
- Stream processing with Apache Spark
- Interactive dashboard with live metrics
- Schema management with Schema Registry
- Docker containerization
- Configuration management
- Confluent Control Center monitoring

## Quick Start

### Prerequisites
- Docker Desktop for Mac
- Docker Compose
- Make

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd kafka-ecommerce-platform
   ```

2. **Start the platform**
   ```bash
   make up
   ```

3. **Access services**
   - Control Center: http://localhost:9021
   - Dashboard: http://localhost:8501

### Component Status
```bash
# Check all services
docker-compose ps

# View logs
make logs
```

## Components

### Data Generator
- Generates realistic ecommerce events
- Uses Avro schemas for data consistency
- Configurable event rates and patterns

### Kafka Producer
- Streams events to Kafka topics
- Schema Registry integration
- Configurable batch sizes and intervals

### Kafka Consumer
- Real-time event processing
- Schema-aware deserialization
- Error handling and retry logic

### Spark Processor
- Stream processing with structured streaming
- Real-time analytics calculations
- Integration with Kafka and Schema Registry

### Dashboard
- Real-time metrics visualization
- Interactive charts and graphs
- Auto-refresh capability

## Configuration

### Environment Variables

```bash
# For local development (outside Docker)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=ecommerce-events

# For Docker containers (set in docker-compose.yml)
KAFKA_BOOTSTRAP_SERVERS=broker:29092
KAFKA_TOPIC=ecommerce-events
```

---

## Python Virtual Environment Setup

It is recommended to use a Python virtual environment for local development:

```bash
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Development

### Local Development

```bash

# Build docker images for kafka producer and kafka consumer (if you haven't already)
make build

# Start all services (Kafka broker, producer, consumer)
make up

# Run the spark processor
make processor

# Run the streamlit dashboard
make dashboard 

# View logs
make logs

# Stop services
make down

# Clean the setup 
make clean

```

### Running Producer and Consumer Locally

```bash
# In one terminal
python src/kafka_producer.py

# In another terminal
python src/kafka_consumer.py
```

---

## Monitoring

To list Kafka topics:

```bash
docker exec broker kafka-topics --bootstrap-server localhost:9092 --list
```

To view messages in a topic:

```bash
docker exec -it broker kafka-console-consumer --bootstrap-server localhost:9092 --topic ecommerce-events --from-beginning
```
---

## Troubleshooting

- If you see errors about replication factor or internal topics, you can ignore them for single-broker local development.
- Ensure your Python scripts use `localhost:9092` when running outside Docker, and `broker:29092` when running inside Docker containers.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request
