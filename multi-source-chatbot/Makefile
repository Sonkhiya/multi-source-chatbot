.PHONY: help install dev test run docker-build docker-up docker-down clean logs

help:
	@echo "Multi-Source Chatbot - Available Commands"
	@echo "=========================================="
	@echo "make install       - Install dependencies"
	@echo "make dev           - Run in development mode"
	@echo "make test          - Run tests"
	@echo "make docker-build  - Build Docker image"
	@echo "make docker-up     - Start Docker containers"
	@echo "make docker-down   - Stop Docker containers"
	@echo "make docker-logs   - View Docker logs"
	@echo "make clean         - Clean cache and build files"
	@echo "make logs          - View application logs"

install:
	pip install -r requirements.txt

dev:
	python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=src

docker-build:
	docker-compose -f docker/docker-compose.yml build

docker-up:
	docker-compose -f docker/docker-compose.yml up -d

docker-down:
	docker-compose -f docker/docker-compose.yml down

docker-logs:
	docker-compose -f docker/docker-compose.yml logs -f chatbot

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

logs:
	tail -f logs/chatbot.log
