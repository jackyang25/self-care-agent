# AGENTS.md

Instructions for AI coding agents working on this project.

## Project Overview

Healthcare self-care agent prototype using LangGraph for multi-step reasoning and tool chaining. The system helps users access health services and commodities in low and middle income country settings.

**Key Architecture:**
- LangGraph agent with native tool calling
- PostgreSQL database for user data and interactions
- Streamlit interface for user interaction
- Docker-based development environment

**Important:** This is a prototype. Tool responses contain mocked data, but input/output schemas represent architectural slots for future integration.

## Setup Commands

### Initial Setup

1. **Start Docker containers:**
   ```bash
   make up
   ```

2. **Create database tables:**
   ```bash
   make create-tables
   ```

3. **Seed database (optional):**
   ```bash
   make seed-db
   ```

4. **Set environment variables:**
   - Copy `.env.example` to `.env` (if exists)
   - Set `OPENAI_API_KEY=your_key_here`
   - Optional: `LLM_MODEL=gpt-4o` (default), `TEMPERATURE=0.3` (default)

### Development Workflow

- **Start services:** `make up` or `make dev` (build + logs)
- **View logs:** `make logs` or `make logs-app`
- **Restart app:** `make change` (for code changes)
- **Stop services:** `make down`
- **Reset database:** `make reset-db` (destructive)

### Local Development (without Docker)

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables** (see above)

4. **Run application:**
   ```bash
   python streamlit_server.py
   ```

## Code Style

### Python Conventions

- **Comments:** Lowercase, concise, purposeful. Only add when necessary for understanding.
- **Docstrings:** Use triple-quoted strings for module/function/class documentation.
- **Imports:** Group by standard library, third-party, local imports.
- **Type Hints:** Use `Optional`, `TypedDict`, `Annotated` from `typing` where appropriate.
- **Naming:** snake_case for functions/variables, PascalCase for classes.

### Code Organization

- **Tools:** Each tool in `src/tools/` with its own file
- **Utils:** Shared utilities in `src/utils/`
- **Scripts:** Database scripts in `scripts/`
- **Documentation:** Human-facing docs in `docs/`

### Important Patterns

- **Context Variables:** Use `contextvars.ContextVar` for thread-safe user context (see `src/utils/context.py`)
- **Tool Responses:** Triage tool returns structured JSON; other tools return strings (see `docs/tools.md`)
- **Error Handling:** Tools should handle missing/invalid inputs gracefully
- **Logging:** Use `src/utils/logger.py` for consistent logging

## Testing Instructions

### Database Testing

- **Test connection:** `make test-db` (in container) or `make test-db-local` (local)
- **Check and seed:** `make seed-db-auto` (automatically seeds if empty)

### Manual Testing

1. Start services: `make up`
2. Access Streamlit UI at `http://localhost:8501`
3. Test user login (demo: `jack.yang@gatesfoundation.org`)
4. Test tool chaining patterns (see `docs/testing.md` for examples)

### Before Committing

- Ensure database scripts work: `make create-tables` and `make seed-db`
- Check that app starts: `make up` and verify UI loads
- Review code follows style guidelines (lowercase comments, proper structure)

## Project Structure

```
.
├── streamlit_server.py     # Streamlit UI server entry point
├── webhook_server.py       # FastAPI webhook server entry point
├── src/
│   ├── agent.py           # LangGraph agent with tool calling
│   ├── channels/
│   │   ├── streamlit.py   # Streamlit channel handler
│   │   └── whatsapp.py    # WhatsApp channel handler
│   ├── db.py              # Database connection utilities
│   ├── tools/             # Tool implementations
│   │   ├── triage.py      # Triage and risk flagging
│   │   ├── commodity.py  # Commodity orders
│   │   ├── pharmacy.py   # Pharmacy orders
│   │   ├── referrals.py  # Referrals and scheduling
│   │   └── database.py   # Database queries
│   └── utils/             # Shared utilities
│       ├── context.py     # Context variables
│       ├── interactions.py # Interaction storage
│       └── logger.py      # Logging utilities
├── scripts/               # Database management scripts
│   ├── db_create_tables.py
│   ├── db_seed.py
│   ├── db_check_and_seed.py
│   └── db_test_connection.py
├── docs/                  # Human-facing documentation
│   ├── agent.md          # Agent architecture
│   ├── tools.md          # Tool documentation
│   ├── database.md       # Database schema
│   └── fixtures.md       # Fixture data structure
├── fixtures/             # Seed data
│   └── seed_data.json
├── docker-compose.yml     # Docker services
├── Dockerfile            # App container image
└── Makefile             # Common commands
```

## Database Management

### Common Commands

- **Create tables:** `make create-tables`
- **Seed data:** `make seed-db` (idempotent)
- **Auto-seed:** `make seed-db-auto` (checks if empty first)
- **Clear and reseed:** `make seed-db-clear` (destructive)
- **Reset completely:** `make reset-db` (deletes all data)

### Database Access

- **PostgreSQL:** `localhost:5432` (user: `postgres`, password: `postgres`, db: `selfcare`)
- **pgAdmin:** `http://localhost:5050` (email: `admin@admin.com`, password: `admin`)
- **Shell access:** `make shell-db` (opens psql)

## Important Conventions

### Tool Development

- **Structured Responses:** Triage tool returns JSON; others return strings (see `src/tools/triage.py` for example)
- **Context Access:** Tools access current user via `current_user_id.get()` from `src/utils/context.py`
- **Tool Registration:** All tools must be added to `src/tools/__init__.py` in `TOOLS` list
- **Input Schemas:** Use Pydantic `BaseModel` for tool inputs (see existing tools)

### Agent Development

- **System Prompt:** Located in `src/agent.py` as `SYSTEM_PROMPT` constant
- **State Management:** Agent state uses `TypedDict` with `Annotated` for message accumulation
- **Tool Chaining:** Agent automatically chains tools based on results (see `docs/agent.md`)
- **Interaction Storage:** All interactions automatically saved via `save_interaction()` in `src/utils/interactions.py`

### Documentation

- **For Humans:** `docs/` folder (agent.md, tools.md, database.md)
- **For Agents:** This file (`AGENTS.md`)
- **Architectural Notes:** Document prototype vs. production slots clearly

## Security Considerations

- **User Context:** Tools automatically use current user from context (no manual user_id passing needed)
- **Database:** All queries should use parameterized queries (via `get_db_cursor()`)
- **API Keys:** Never commit `.env` file or hardcode API keys
- **User Data:** Tools can only access current logged-in user's data

## Common Tasks

### Adding a New Tool

1. Create tool file in `src/tools/` (e.g., `src/tools/new_tool.py`)
2. Define Pydantic input schema
3. Implement tool function
4. Create `StructuredTool` instance
5. Add to `TOOLS` list in `src/tools/__init__.py`
6. Document in `docs/tools.md`

### Modifying System Prompt

1. Edit `SYSTEM_PROMPT` in `src/agent.py`
2. Follow context engineering best practices (hierarchical structure, reduce redundancy)
3. Test tool calling behavior after changes
4. Update `docs/agent.md` if architecture changes

### Database Schema Changes

1. Update `scripts/db_create_tables.py`
2. Run `make create-tables` to apply changes
3. Update seed data in `fixtures/seed_data.json` if needed
4. Document changes in `docs/database.md`

## Troubleshooting

### App won't start

- Check Docker containers: `make ps`
- Check logs: `make logs-app`
- Verify environment variables: `make shell` then `env | grep OPENAI`

### Database connection issues

- Test connection: `make test-db`
- Check database is running: `make ps`
- Verify credentials in `docker-compose.yml`

### Tool not being called

- Check system prompt emphasizes tool usage
- Verify tool is in `TOOLS` list
- Check logs for tool call attempts: `make logs-app`
- Review `docs/agent.md` for tool chaining patterns

## References

- **Agent Architecture:** `docs/agent.md`
- **Tool Documentation:** `docs/tools.md`
- **Database Schema:** `docs/database.md`
- **Testing Guide:** `docs/testing.md`

