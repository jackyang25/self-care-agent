.PHONY: help setup dev up down restart ps logs shell shell-db create-tables seed-db reset-db test-db rebuild clean

# ==============================================================================
# Help
# ==============================================================================

help: ## show this help message
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ==============================================================================
# Quick Start
# ==============================================================================

setup: ## first-time setup (start containers, create tables, seed data)
	docker-compose up -d
	@echo "Waiting for database to be ready..."
	@sleep 5
	$(MAKE) create-tables
	$(MAKE) seed-db
	@echo ""
	@echo "Setup complete! Access the app at http://localhost:8501"

dev: ## start in development mode (build + follow logs)
	docker-compose up -d --build
	docker-compose logs -f

# ==============================================================================
# Container Management
# ==============================================================================

up: ## start all containers
	docker-compose up -d

down: ## stop all containers
	docker-compose down

restart: ## restart all containers
	docker-compose restart

ps: ## show running containers
	docker-compose ps

logs: ## follow logs from all containers
	docker-compose logs -f

logs-app: ## follow logs from app containers only
	docker-compose logs -f streamlit webhook

shell: ## open bash shell in app container
	docker-compose exec streamlit /bin/bash

# ==============================================================================
# Database Management
# ==============================================================================

create-tables: ## create all database tables (app + RAG)
	docker-compose exec streamlit python scripts/db/create_tables.py

seed-db: ## seed database with demo data (idempotent, safe to rerun)
	docker-compose exec streamlit python scripts/db/seed.py

reset-db: ## reset database (delete all data, recreate tables, reseed)
	docker-compose down -v
	docker-compose up -d
	@echo "Waiting for database..."
	@sleep 5
	$(MAKE) create-tables
	$(MAKE) seed-db

test-db: ## test database connection
	docker-compose exec streamlit python scripts/db/test.py

shell-db: ## open postgres shell
	docker-compose exec db psql -U postgres -d selfcare

# ==============================================================================
# Advanced
# ==============================================================================

rebuild: ## rebuild and restart all containers (force recreate)
	docker-compose up -d --build --force-recreate

clean: ## stop containers, remove volumes, and clean docker system
	docker-compose down -v
	docker system prune -f

