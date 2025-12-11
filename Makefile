.PHONY: help up down restart change logs build rebuild clean ps status shell shell-db watch

help: ## show this help message
	@echo "available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## start all containers
	docker-compose up -d

up-build: ## start containers and rebuild images
	docker-compose up -d --build

down: ## stop all containers
	docker-compose down

down-volumes: ## stop containers and remove volumes (deletes database data)
	docker-compose down -v

restart: ## restart all containers
	docker-compose restart

change: ## restart streamlit container only (for code changes)
	docker-compose restart streamlit

change-webhook: ## restart webhook container only (for code changes)
	docker-compose restart webhook

logs: ## show logs from all containers
	docker-compose logs -f

logs-streamlit: ## show logs from streamlit container only
	docker-compose logs -f streamlit

logs-webhook: ## show logs from webhook container only
	docker-compose logs -f webhook

logs-db: ## show logs from database container only
	docker-compose logs -f db

build: ## build images without cache
	docker-compose build --no-cache

rebuild: ## rebuild and restart containers
	docker-compose up -d --build --force-recreate

clean: ## stop containers, remove volumes, and clean up
	docker-compose down -v
	docker system prune -f

ps: ## show running containers
	docker-compose ps

status: ps ## alias for ps

shell: ## open shell in streamlit container
	docker-compose exec streamlit /bin/bash

shell-webhook: ## open shell in webhook container
	docker-compose exec webhook /bin/bash

shell-db: ## open psql shell in database container
	docker-compose exec db psql -U postgres -d selfcare

test-db: ## test database connection
	docker-compose exec streamlit python scripts/db_test_connection.py

test-db-local: ## test database connection from local machine
	python scripts/db_test_connection.py

create-tables: ## create database tables
	docker-compose exec streamlit python scripts/db_create_tables.py

seed-db: ## seed database with fixture data (idempotent)
	docker-compose exec streamlit python scripts/db_seed.py

seed-db-auto: ## check if database is empty and seed automatically
	docker-compose exec streamlit python scripts/db_check_and_seed.py

seed-db-clear: ## clear all data and reseed (destructive)
	docker-compose exec streamlit python scripts/db_seed.py --clear

reset-db: ## completely reset database (deletes all data)
	docker-compose down -v
	docker-compose up -d
	@echo "waiting for database to be ready..."
	@sleep 5
	docker-compose exec streamlit python scripts/db_create_tables.py
	docker-compose exec streamlit python scripts/db_seed.py

watch: ## start with file watching (requires watchfiles or similar)
	docker-compose up --watch

dev: up-build logs ## start in development mode (build + logs)

stop: down ## alias for down

start: up ## alias for up

