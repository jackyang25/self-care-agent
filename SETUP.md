# Setup Guide

Complete installation and configuration instructions for the Self-Care Agent Framework.

## Prerequisites

**Required:**
- **Docker and Docker Compose** ([download here](https://www.docker.com/products/docker-desktop))
- **OpenAI API key** ([get one here](https://platform.openai.com/api-keys))
- Git

**Note:** This project runs entirely in Docker containers. No local Python or PostgreSQL installation needed.

## Quick Start (5 minutes)

### 1. Clone and Configure

```bash
git clone <repository-url>
cd GH-AI-Self-Care

# Create environment file
cp .env.example .env

# Edit .env and set your OpenAI API key
# OPENAI_API_KEY=your_key_here
```

### 2. Start Services

```bash
make up              # Start Docker containers
make create-tables   # Create database schema
make seed-db         # Load mock users and providers
```

### 3. Access the Application

- **Streamlit UI**: http://localhost:8501
- **pgAdmin**: http://localhost:5050 (email: `admin@admin.com`, password: `admin`)

### 4. Login

Use any seeded user credentials:
- Email: `jack.yang@gatesfoundation.org`
- Phone: `+12066608261`

Or see `seeds/demo.json` for all test users.

### 5. Test the System

Try these interactions:

**Basic triage:**
```
"I have a headache"
```
Agent will triage symptoms and provide appropriate guidance.

**Emergency symptoms:**
```
"I have severe chest pain"
```
Agent will:
- Triage using verified Lean protocol
- Route to appropriate specialist (cardiology)
- Ask for scheduling consent
- Schedule appointment with available provider

**Check appointments:**
```
"Show me my appointments"
```
View scheduled appointments from the database.

## Common Commands

```bash
# Start/stop services
make up              # Start all containers
make down            # Stop all containers
make restart         # Restart all containers

# Logs
make logs            # View all logs
make logs-streamlit  # View Streamlit logs only
make logs-webhook    # View webhook logs only

# Database
make create-tables   # Create database schema
make seed-db         # Seed database (idempotent)
make reset-db        # Reset database (destructive - deletes all data)

# Development
make change          # Restart app containers (after code changes)
make ps              # Show running containers
make shell           # Open shell in Streamlit container
make shell-db        # Open PostgreSQL shell

# Testing
make test-db         # Test database connection

# Help
make help            # Show all available commands
```

## Environment Configuration

### Required Variables

```bash
# .env file
OPENAI_API_KEY=your_key_here              # Required
LLM_MODEL=gpt-4o                          # Optional (default: gpt-4o)
TEMPERATURE=0.3                           # Optional (default: 0.3)
```

### Optional: LangSmith for Observability

To enable LLM tracing, cost monitoring, and debugging:

```bash
# Add to .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key      # Get from https://smith.langchain.com/
LANGCHAIN_PROJECT=scaf-poc
```

After adding, restart: `make change`

Benefits:
- View every tool call and LLM interaction
- Track token usage and costs per conversation
- Debug agent decision-making in real-time
- Full audit trail for compliance

### Database Configuration

Default Docker configuration (no changes needed):

```bash
POSTGRES_HOST=db                          # Container name
POSTGRES_PORT=5432
POSTGRES_DB=selfcare
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

These are automatically configured in `docker-compose.yml`.

## WhatsApp Integration (Optional)

To enable WhatsApp channel:

### 1. Set Up ngrok

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/download

# Start ngrok tunnel
make ngrok

# Note the HTTPS URL (e.g., https://abc123.ngrok.io)
```

### 2. Configure WhatsApp Business

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create app and add WhatsApp product
3. Configure webhook:
   - URL: `https://your-ngrok-url.ngrok.io/webhook`
   - Verify token: Set `WHATSAPP_WEBHOOK_SECRET` in `.env`
4. Subscribe to message events

### 3. Update Environment

```bash
# Add to .env
WHATSAPP_WEBHOOK_SECRET=your_verify_token
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
```

### 4. Restart Services

```bash
make change-webhook
```

See [docs/whatsapp.md](docs/whatsapp.md) for detailed WhatsApp setup instructions.

## Database Management

### Viewing Data

**Option 1: pgAdmin Web Interface**
1. Open http://localhost:5050
2. Login with `admin@admin.com` / `admin`
3. Add server:
   - Host: `db`
   - Port: `5432`
   - Database: `selfcare`
   - Username: `postgres`
   - Password: `postgres`

**Option 2: Command Line**
```bash
make shell-db
# Then run SQL queries:
SELECT * FROM users;
SELECT * FROM appointments;
SELECT * FROM interactions ORDER BY created_at DESC LIMIT 10;
```

### Resetting Database

**Warning: This deletes all data**

```bash
make reset-db
```

This will:
1. Stop containers
2. Delete database volume
3. Restart containers
4. Recreate all tables
5. Reseed with fixture data

### Manual Database Scripts

```bash
# Create tables only
docker-compose exec streamlit python scripts/db/create_tables.py

# Seed data only
docker-compose exec streamlit python scripts/db/seed.py

# Clear and reseed
docker-compose exec streamlit python scripts/db/seed.py --clear

# Test connection
docker-compose exec streamlit python scripts/db/test.py
```

## Troubleshooting

### Docker Issues

**Containers won't start:**
```bash
docker-compose down -v  # Remove volumes
docker system prune -f  # Clean up Docker
make up-build          # Rebuild and start
```

**Port conflicts (8501, 5432, 5050):**
```bash
# Find what's using the port
lsof -i :8501

# Kill the process or change port in docker-compose.yml
```

### Database Issues

**Can't connect to database:**
```bash
# Check if database is running
make ps

# Check logs
make logs-db

# Test connection
make test-db
```

**Tables don't exist:**
```bash
make create-tables
```

**Need fresh data:**
```bash
make reset-db
```

### OpenAI API Issues

**Invalid API key error:**
- Verify key in `.env` file
- Check key is valid at https://platform.openai.com/api-keys
- Restart containers after updating `.env`: `make restart`

**Rate limit errors:**
- Check your OpenAI usage limits
- Consider upgrading your OpenAI plan
- Reduce `TEMPERATURE` in `.env` (doesn't help rate limits but uses fewer tokens)

### Application Issues

**Streamlit won't load:**
```bash
# Check logs
make logs-streamlit

# Restart containers
make change-streamlit

# If code changed, rebuild
make up-build
```

**User not found:**
- Check you're using a seeded user email/phone
- List available users:
  ```bash
  make shell-db
  SELECT email, phone_e164 FROM users;
  ```

**Appointments not saving:**
- Check logs for errors: `make logs-streamlit`
- Verify tables exist: `make shell-db` then `\dt`
- Reseed database: `make reset-db`

## Development Workflow

### Making Code Changes

1. **Edit code** in `src/` directory
2. **Restart app** containers:
   ```bash
   make change  # Restarts streamlit and webhook
   ```
3. **View logs** to debug:
   ```bash
   make logs-streamlit
   ```

**Note:** Code is mounted as a volume, so changes are reflected after restart (no rebuild needed).

### Adding New Tools

1. Create tool file in `src/tools/`
2. Define Pydantic input schema
3. Implement tool function
4. Create `StructuredTool` instance
5. Add to `TOOLS` list in `src/tools/__init__.py`
6. Restart: `make change`

See [AGENTS.md](AGENTS.md) for detailed development instructions.

### Database Schema Changes

1. Update `scripts/db/create_tables.py`
2. Update `scripts/db/seed.py` if needed
3. Update `seeds/demo.json` if needed
4. Reset database:
   ```bash
   make reset-db
   ```

### Testing Changes

```bash
# Start fresh
make down
make up
make create-tables
make seed-db

# Test in UI
open http://localhost:8501

# Check logs
make logs-streamlit
```

## Production Deployment Considerations

This setup is for **development and POC** only. For production:

### Security
- [ ] Use secrets management (AWS Secrets Manager, Azure Key Vault)
- [ ] Enable PostgreSQL SSL
- [ ] Set up proper authentication (not mock login)
- [ ] Add rate limiting and DDoS protection
- [ ] Enable HTTPS for all endpoints

### Scalability
- [ ] Use managed PostgreSQL (AWS RDS, Azure Database)
- [ ] Deploy with container orchestration (Kubernetes, ECS)
- [ ] Add Redis for session management
- [ ] Implement connection pooling
- [ ] Add load balancing

### Monitoring
- [ ] Set up logging aggregation (CloudWatch, Datadog)
- [ ] Add error tracking (Sentry)
- [ ] Configure health checks
- [ ] Set up alerting for critical errors

### Data
- [ ] Implement backup strategy
- [ ] Set up disaster recovery
- [ ] Add data retention policies
- [ ] Enable audit logging

## Support

For setup issues:
1. Check [Troubleshooting](#troubleshooting) section above
2. Review logs: `make logs`
3. Check [docs/](docs/) for component-specific documentation
4. Contact: jack.yang@gatesfoundation.org

## Next Steps

After setup is complete:
- **[README.md](README.md)** - Project overview and POC achievements
- **[docs/agent.md](docs/agent.md)** - LangGraph architecture and tool calling
- **[docs/tools.md](docs/tools.md)** - Tool specifications and usage
- **[docs/database.md](docs/database.md)** - Database schema and queries
- **[docs/triage-verification.md](docs/triage-verification.md)** - Verified triage with Lean
- **[docs/rag.md](docs/rag.md)** - RAG architecture and clinical grounding
- **[docs/whatsapp.md](docs/whatsapp.md)** - WhatsApp integration guide
- **[AGENTS.md](AGENTS.md)** - Developer guidelines for AI agents

