.PHONY: help build up down logs restart test clean shell-fastapi shell-postgres

help:
	@echo "Tutor Platform Backend - Available Commands"
	@echo "=============================================="
	@echo ""
	@echo "Infrastructure:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make clean          - Stop and remove containers, volumes, images"
	@echo "  make verify         - Verify infrastructure setup"
	@echo ""
	@echo "Logs & Debugging:"
	@echo "  make logs           - View all logs (follow mode)"
	@echo "  make logs-fastapi   - View FastAPI logs"
	@echo "  make logs-postgres  - View PostgreSQL logs"
	@echo "  make logs-keycloak  - View Keycloak logs"
	@echo ""
	@echo "Container Access:"
	@echo "  make shell-fastapi  - Open bash shell in FastAPI container"
	@echo "  make shell-postgres - Open psql shell in PostgreSQL container"
	@echo ""
	@echo "Development:"
	@echo "  make test           - Run tests"
	@echo "  make format         - Format Python code (black)"
	@echo "  make lint           - Run linter (flake8)"
	@echo ""

build:
	@echo "Building Docker images..."
	docker-compose build

up:
	@echo "Starting services..."
	docker-compose up -d
	@echo "✅ Services started. Check: docker-compose ps"

down:
	@echo "Stopping services..."
	docker-compose down

restart: down up
	@echo "✅ Services restarted"

logs:
	docker-compose logs -f

logs-fastapi:
	docker-compose logs -f fastapi

logs-postgres:
	docker-compose logs -f postgres

logs-keycloak:
	docker-compose logs -f keycloak

shell-fastapi:
	docker-compose exec fastapi bash

shell-postgres:
	docker-compose exec postgres psql -U tutordb_user -d tutor_platform_db

verify:
	@bash verify-infrastructure.sh

test:
	@echo "Running tests..."
	docker-compose exec fastapi pytest src/tests/ -v

format:
	@echo "Formatting code..."
	docker-compose exec fastapi black src/

lint:
	@echo "Running linter..."
	docker-compose exec fastapi flake8 src/

clean: down
	@echo "Removing containers and volumes..."
	docker-compose down -v
	@echo "✅ Cleaned up"

.DEFAULT_GOAL := help
