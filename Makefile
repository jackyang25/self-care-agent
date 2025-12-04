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

change: ## restart app container only (for code changes)
	docker-compose restart app

logs: ## show logs from all containers
	docker-compose logs -f

logs-app: ## show logs from app container only
	docker-compose logs -f app

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

shell: ## open shell in app container
	docker-compose exec app /bin/bash

shell-db: ## open psql shell in database container
	docker-compose exec db psql -U postgres -d selfcare

watch: ## start with file watching (requires watchfiles or similar)
	docker-compose up --watch

dev: up-build logs ## start in development mode (build + logs)

stop: down ## alias for down

start: up ## alias for up

