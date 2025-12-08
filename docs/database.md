# Database Management

## Design: Persistent Database with Optional Seeding

The database is **persistent by default** - data survives container restarts. This is the recommended approach for development.

## Quick Start

### First Time Setup
```bash
# start containers
make up

# seed database with fixture data
make seed-db
```

### Daily Development
```bash
# just start containers (data persists)
make up

# or restart if needed
make restart
```

## Database Commands

### Seeding
```bash
# seed database (idempotent - won't duplicate data)
make seed-db

# check if empty and seed automatically
make seed-db-auto

# clear all data and reseed (destructive)
make seed-db-clear
```

### Reset Database
```bash
# completely reset database (deletes all data)
make reset-db
# or manually:
make down-volumes
make up
make seed-db
```

### Testing Connection
```bash
# test database connection
make test-db
```

## Database Persistence

- **Default**: Database data persists in Docker volume `postgres_data`
- **Data survives**: Container restarts, code changes, app restarts
- **To clear**: Use `make down-volumes` or `make reset-db`

## Fixture Files

Fixture data is in `src/fixtures/`:
- `seed_data.json` - default seed data
- Add more fixture files as needed

See `src/fixtures/README.md` for fixture templates and structure.

