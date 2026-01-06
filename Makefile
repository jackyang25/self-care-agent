.PHONY: help setup start stop restart rebuild logs clean reset db-shell db-create db-seed

# ============================================================================
# Help
# ============================================================================

help:
	@echo "AI Self-Care Agent - Available Commands:"
	@echo ""
	@echo "Setup:"
	@echo "  make setup       - First-time setup (start containers, create tables, seed data)"
	@echo ""
	@echo "Docker Containers:"
	@echo "  make start       - Start Docker containers"
	@echo "  make stop        - Stop Docker containers"
	@echo "  make restart     - Restart Docker containers"
	@echo "  make rebuild     - Rebuild and restart containers (use after dependency changes)"
	@echo "  make logs        - View container logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean       - Stop containers and remove them"
	@echo "  make reset       - Reset database with seed data"
	@echo ""
	@echo "Database:"
	@echo "  make db-shell    - Access PostgreSQL command line"
	@echo "  make db-create   - Create database tables"
	@echo "  make db-seed     - Seed database with demo data"
	@echo ""
	@echo "Admin Tools:"
	@echo "  make redis-shell - Access Redis command line"
	@echo "  make redis-clear - Clear Redis cache"
	@echo ""
	@echo "Web Interfaces:"
	@echo "  Streamlit UI:     http://localhost:8501"
	@echo "  pgAdmin:          http://localhost:5050  (admin@admin.com / admin)"
	@echo "  RedisInsight:     http://localhost:5540"
	@echo ""

# ============================================================================
# Setup
# ============================================================================

# first-time setup with database initialization
setup:
	@echo "Starting first-time setup..."
	@docker-compose up -d
	@echo "Waiting for database to be ready..."
	@sleep 5
	@$(MAKE) db-create
	@$(MAKE) db-seed
	@echo ""
	@echo "✓ Setup complete! Access the app at http://localhost:8501"

# ============================================================================
# Docker Containers
# ============================================================================

# start all containers in background
start:
	@echo "Starting containers..."
	@docker-compose up -d
	@echo "✓ Containers started"

# stop containers but keep volumes (data persists)
stop:
	@echo "Stopping containers..."
	@docker-compose down
	@echo "✓ Containers stopped"

# restart containers without recreating them
restart:
	@echo "Restarting containers..."
	@docker-compose restart
	@echo "✓ Containers restarted"

# rebuild containers from scratch (use after dependency changes)
rebuild:
	@echo "Rebuilding containers..."
	@docker-compose build --no-cache
	@docker-compose up -d
	@echo "✓ Containers rebuilt and started"

# view live logs from all containers
logs:
	@docker-compose logs -f

# ============================================================================
# Cleanup
# ============================================================================

# stop and remove containers but keep volumes (data persists)
clean:
	@echo "Cleaning up containers..."
	@docker-compose down
	@echo "✓ Containers removed"

# stop containers and delete all data (fresh start)
reset:
	@echo "WARNING: This will delete all database data!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "Resetting everything..."
	@docker-compose down -v
	@docker-compose up -d
	@echo "Waiting for database..."
	@sleep 5
	@$(MAKE) db-create
	@$(MAKE) db-seed
	@echo "✓ Database reset complete"

# ============================================================================
# Database
# ============================================================================

# open postgresql command line interface
db-shell:
	@docker-compose exec postgres psql -U postgres -d selfcare

# create database tables
db-create:
	@echo "Creating database tables..."
	@docker-compose exec streamlit python scripts/create_tables.py
	@echo "✓ Tables created"

# seed database with demo data
db-seed:
	@echo "Seeding database with demo data..."
	@docker-compose exec streamlit python scripts/seed_database.py
	@echo "✓ Database seeded"

# open redis command line interface
redis-shell:
	@docker-compose exec redis redis-cli

# clear redis cache
redis-clear:
	@echo "Clearing Redis cache..."
	@docker-compose exec redis redis-cli FLUSHDB
	@echo "✓ Redis cache cleared"
