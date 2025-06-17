# Kafka Ecommerce Analytics Platform

A comprehensive real-time ecommerce analytics platform built with Confluent Kafka, running locally with Docker Compose.

## Architecture

- **Confluent Kafka**: Message streaming platform
- **Schema Registry**: Schema management and evolution
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
   make up-build
   ```

3. **Access services**
   - Control Center: http://localhost:9021
   - Dashboard: http://localhost:8501
   - Schema Registry: http://localhost:8081

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
KAFKA_BOOTSTRAP_SERVERS=broker:29092
SCHEMA_REGISTRY_URL=http://schema-registry:8081
KAFKA_TOPIC=ecommerce-events
```

## Development

### Local Development
```bash
# Start all services
make up

# Rebuild and start
make up-build

# View logs
make logs

# Stop services
make down
```

### Testing
```bash
# Run tests
pytest tests/

# Linting
flake8 src/
```

## Monitoring

Access Confluent Control Center at http://localhost:9021 for:
- Topic management
- Consumer group monitoring
- Schema Registry management
- Cluster health metrics

## Troubleshooting

### Common Issues

1. **Kafka Connection Issues**
   ```bash
   docker-compose logs broker
   ```

2. **Schema Registry Issues**
   ```bash
   docker-compose logs schema-registry
   ```

3. **Producer/Consumer Issues**
   ```bash
   docker-compose logs producer
   docker-compose logs consumer
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request
