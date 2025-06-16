#!/bin/bash
set -e

# Clean up existing cluster
kind delete cluster --name kafka-cluster 2>/dev/null || true

# Create new cluster
echo "Creating Kind cluster..."
kind create cluster --config k8s/kind-config.yaml

echo "Creating kafka namespace..."
kubectl create namespace kafka

echo "Adding Bitnami repo..."
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

echo "Installing Kafka..."
helm install kafka bitnami/kafka \
  --namespace kafka \
  --set broker.replicaCount=1 \
  --set controller.replicaCount=1 \
  --set zookeeper.replicaCount=1 \
  --set externalAccess.enabled=true \
  --set externalAccess.autoDiscovery.enabled=false \
  --set externalAccess.service.type=NodePort \
  --set externalAccess.service.nodePorts[0]=9092 \
  --set externalAccess.service.loadBalancerIPs={127.0.0.1} \
  --set containerPorts.client=9092 \
  --set listeners.client.protocol=PLAINTEXT \
  --set broker.nodeSelector.kubernetes\\.io/hostname=kafka-cluster-control-plane

# Wait for Kafka to be ready
echo "Waiting for Kafka to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kafka -n kafka --timeout=300s

# Create ConfigMap with Python code
echo "Creating ConfigMap with Python code..."
kubectl create configmap python-code \
  --from-file=src/kafka_producer.py \
  --from-file=src/kafka_consumer.py \
  --from-file=src/data_generator.py \
  --from-file=src/config.py \
  -n kafka

# Deploy producer and consumer
echo "Deploying producer and consumer..."
kubectl apply -f k8s/producer-consumer.yaml

echo "Setup complete! Check pods with: kubectl get pods -n kafka"