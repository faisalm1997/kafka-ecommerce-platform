# Kafka Ecommerce Analytics Platform

A comprehensive real-time ecommerce analytics platform built with Apache Kafka, running on Kubernetes (KIND) with automated deployment and CI/CD pipelines.

## Architecture

- **Kafka**: Message streaming platform
- **Zookeeper**: Kafka coordination service
- **Producer**: Generates mock ecommerce events
- **Consumer**: Processes individual events
- **Spark Processor**: Real-time stream processing and analytics
- **Dashboard**: Streamlit-based real-time visualization
- **KIND**: Local Kubernetes development cluster

## Features

- Real-time ecommerce event generation (orders, page views, cart actions)
- Stream processing with Apache Spark
- Interactive dashboard with live metrics
- Automated deployment with Kubernetes
- CI/CD pipeline with GitHub Actions
- Docker containerization
- Configuration management

## Quick Start

### Prerequisites
- Docker
- KIND (Kubernetes in Docker)
- kubectl
- Make

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd kafka-ecommerce-platform
   ```

2. **Run complete setup**
   ```bash
   make all
   ```

3. **Access services**
   - Dashboard: http://localhost:8501
   - Kafka: localhost:9092

### Manual Setup Steps

```bash
# Create KIND cluster
make setup-kind

# Deploy Kafka
make deploy-kafka

# Build and load Docker images
make build-images

# Deploy applications
make deploy-apps

# Setup port forwarding
make port-forward
```

## Components

### Data Generator
Generates realistic ecommerce events:
- Customer orders with products and pricing
- Page view tracking
- Shopping cart interactions
- Configurable event rates

### Kafka Producer
- Streams events to Kafka topics
- Configurable batch sizes and intervals
- Proper partitioning by customer ID

### Kafka Consumer
- Processes events in real-time
- Scalable consumer groups
- Error handling and retry logic

### Spark Processor
- Real-time stream processing
- Windowed aggregations
- Analytics calculations:
  - Revenue by category
  - Order counts and averages
  - Customer activity by geography

### Dashboard
- Real-time metrics display
- Interactive charts and graphs
- Configurable time windows
- Auto-refresh capability

## Configuration

### Environment Variables (.env)
```bash
KAFKA_BOOTSTRAP_SERVERS=kafka-service:9092
KAFKA_TOPIC=ecommerce-events
DATA_INTERVAL=1
BATCH_SIZE=10
DASHBOARD_REFRESH=5
```

### Python Configuration (config.py)
Centralized configuration management with:
- Kafka settings
- Spark configuration
- Database connections
- Application parameters

## Development

### Local Development with Docker Compose
```bash
docker-compose up -d
```

### Testing
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ --cov=src/

# Linting
flake8 src/
```

### Adding New Event Types
1. Extend `EcommerceDataGenerator` class
2. Update event processing in consumer
3. Add Spark processing logic
4. Update dashboard visualizations

## Deployment

### KIND (Local)
```bash
make all
```

### Production Kubernetes
Update image references in k8s manifests and apply:
```bash
kubectl apply -f k8s/
```

## CI/CD Pipeline

The GitHub Actions workflow includes:
- Code testing and linting
- Docker image building
- Container registry push
- Automated deployment to dev/prod environments

### Triggers
- Push to `main`: Production deployment
- Push to `develop`: Development deployment
- Pull requests: Testing only

## Monitoring

### Kafka Monitoring
- Topic metrics
- Consumer lag
- Throughput statistics

### Application Monitoring
- Event processing rates
- Error rates and retry counts
- Resource utilization

## Scaling

### Horizontal Scaling
- Multiple Kafka brokers
- Consumer group scaling
- Spark executor scaling

### Vertical Scaling
- Resource limits in Kubernetes
- JVM heap sizing for Spark
- Memory allocation optimization

## Troubleshooting

### Common Issues

1. **Kafka Connection Issues**
   ```bash
   kubectl logs -n kafka deployment/kafka
   kubectl port-forward svc/kafka-service 9092:9092 -n kafka
   ```

2. **Consumer Lag**
   ```bash
   # Check consumer group status
   kubectl exec -it kafka-pod -n kafka -- kafka-consumer-groups.sh \
     --bootstrap-server localhost:9092 --describe --group ecommerce-processors
   ```

3. **Dashboard Not Loading**
   ```bash
   kubectl logs -n kafka deployment/dashboard
   kubectl port-forward svc/dashboard-service 8501:8501 -n kafka
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request
