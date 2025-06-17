.PHONY: build up down logs clean

# Build Docker images
build:
	docker build -f docker/Dockerfile.producer 	-t ecommerce-producer:latest .
	docker build -f docker/Dockerfile.consumer 	-t ecommerce-consumer:latest .
	docker build -f docker/Dockerfile.dashboard -t ecommerce-dashboard:latest .
	docker build -f docker/Dockerfile.processor -t ecommerce-processor:latest .

# Start the entire stack
up:
	docker-compose up -d

# Start with build
up-build:
	docker-compose up -d --build

# Stop the stack
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Clean up
clean:
	docker-compose down -v
	docker system prune -f