.PHONY: help setup-kind deploy-kafka build-images deploy-apps port-forward clean

help:
	@echo "Available commands:"
	@echo "  setup-kind      - Create KIND cluster and setup ingress"
	@echo "  deploy-kafka    - Deploy Kafka and Zookeeper to KIND"
	@echo "  build-images    - Build Docker images for Python applications"
	@echo "  deploy-apps     - Deploy all applications (producer, consumer, processor, dashboard)"
	@echo "  port-forward    - Setup port forwarding for services"
	@echo "  clean          - Clean up everything"
	@echo "  all            - Run complete setup"

setup-kind:
	@echo "Creating KIND cluster..."
	kind create cluster --name kafka-cluster --config kind-config.yaml
	@echo "Installing ingress controller..."
	kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
	kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=90s

deploy-kafka:
	@echo "Deploying Kafka..."
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/kafka/
	@echo "Waiting for Kafka to be ready..."
	kubectl wait --for=condition=ready pod -l app=kafka -n kafka --timeout=300s

build-images:
	@echo "Building Docker images..."
	docker build -t ecommerce-producer:latest -f docker/Dockerfile.producer .
	docker build -t ecommerce-consumer:latest -f docker/Dockerfile.consumer .
	docker build -t ecommerce-processor:latest -f docker/Dockerfile.processor .
	docker build -t ecommerce-dashboard:latest -f docker/Dockerfile.dashboard .
	@echo "Loading images into KIND..."
	kind load docker-image ecommerce-producer:latest --name kafka-cluster
	kind load docker-image ecommerce-consumer:latest --name kafka-cluster
	kind load docker-image ecommerce-processor:latest --name kafka-cluster
	kind load docker-image ecommerce-dashboard:latest --name kafka-cluster

deploy-apps:
	@echo "Deploying applications..."
	kubectl apply -f k8s/apps/

port-forward:
	@echo "Setting up port forwarding..."
	kubectl port-forward svc/kafka-service 9092:9092 -n kafka &
	kubectl port-forward svc/dashboard-service 8501:8501 -n kafka &
	@echo "Kafka available at localhost:9092"
	@echo "Dashboard available at localhost:8501"

clean:
	@echo "Cleaning up..."
	kind delete cluster --name kafka-cluster
	docker rmi -f ecommerce-producer:latest ecommerce-consumer:latest ecommerce-processor:latest ecommerce-dashboard:latest

all: setup-kind deploy-kafka build-images deploy-apps port-forward