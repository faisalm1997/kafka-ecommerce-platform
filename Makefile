.PHONY: build up down logs clean processor dashboard

build:
	docker build -f docker/Dockerfile.producer -t ecommerce-producer:latest .
	docker build -f docker/Dockerfile.consumer -t ecommerce-consumer:latest .

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

processor:
	python src/spark_processor.py

dashboard:
	streamlit run src/streamlit_dashboard.py

clean:
	docker-compose down -v
	docker system prune -f