#!/bin/bash
# Database seeding script - initializes database with seed data
# Usage: ./scripts/seed_database.sh (run inside docker container)

set -e  # Exit on any error

echo "=============================================="
echo "  Initializing Database - GH AI Self-Care"
echo "=============================================="
echo ""

# Database connection details (inside docker network)
DB_HOST=${DB_HOST:-postgres}
DB_USER=${DB_USER:-postgres}
DB_NAME=${DB_NAME:-selfcare}

# Check if database is running
echo "Checking database connection..."
if ! psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1" > /dev/null 2>&1; then
    echo "ERROR: Cannot connect to database at $DB_HOST"
    echo "   Waiting a bit longer for database to initialize..."
    sleep 5
    if ! psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1" > /dev/null 2>&1; then
        echo "   Still can't connect. Is PostgreSQL running?"
        exit 1
    fi
fi
echo "Database connected"
echo ""

# Check if OpenAI API key is set (needed for embeddings)
if [ -z "$OPENAI_API_KEY" ]; then
    echo "WARNING: OPENAI_API_KEY not set. Embeddings will fail."
    echo "   Set it in .env or export OPENAI_API_KEY=your_key"
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 1: Seed providers
echo "Step 1: Seeding providers..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f init-db/01_providers.sql
echo ""

# Step 2: Seed sources
echo "Step 2: Seeding sources..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f init-db/02_sources.sql
echo ""

# Step 3: Seed documents (without embeddings)
echo "Step 3: Seeding documents (without embeddings)..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f init-db/03_documents.sql
echo ""

# Step 4: Generate embeddings
echo "Step 4: Generating embeddings via OpenAI..."
python3 scripts/generate_embeddings.py
echo ""

echo "=============================================="
echo "  Database Initialized!"
echo "=============================================="

