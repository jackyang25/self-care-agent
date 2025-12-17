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

## Database Schema

### Connection Details

- **Host**: `localhost` (from host) or `db` (from container)
- **Port**: `5432`
- **Database**: `selfcare`
- **User**: `postgres`
- **Password**: `postgres`
- **pgAdmin**: `http://localhost:5050` (email: `admin@admin.com`, password: `admin`)

### Tables

#### 1. `users`

Stores user profile information.

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | UUID | Primary key |
| `fhir_patient_id` | TEXT | FHIR patient identifier (architectural slot) |
| `primary_channel` | TEXT | Primary communication channel |
| `phone_e164` | TEXT | Phone number in E.164 format |
| `email` | TEXT | Email address |
| `preferred_language` | TEXT | User's preferred language |
| `literacy_mode` | TEXT | Literacy mode preference |
| `country_context_id` | TEXT | Country context identifier (ISO 3166-1 alpha-2 code, e.g., "us", "mx", "ke") (required) |
| `demographics` | JSONB | Demographic data (flexible structure) |
| `accessibility` | JSONB | Accessibility preferences |
| `is_deleted` | BOOLEAN | Soft delete flag (default: false) |
| `created_at` | TIMESTAMP WITH TIME ZONE | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | Last update timestamp |

**Indexes:**
- Primary key on `user_id`
- Foreign key references: `interactions.user_id`, `consents.user_id`

#### 2. `interactions`

Stores all user interactions with the agent, including tool invocations and results.

| Column | Type | Description |
|--------|------|-------------|
| `interaction_id` | UUID | Primary key |
| `user_id` | UUID | Foreign key to `users.user_id` |
| `channel` | TEXT | Communication channel (e.g., `"streamlit"`) |
| `input` | JSONB | User input and tool metadata |
| `protocol_invoked` | TEXT | Protocol name if triage called (e.g., `"triage"`) |
| `protocol_version` | TEXT | Protocol version (e.g., `"1.0"`) |
| `triage_result` | JSONB | Triage assessment results (structured JSON) |
| `risk_level` | TEXT | Extracted risk level (`"low"`, `"medium"`, `"high"`, `"critical"`) |
| `recommendations` | JSONB | Array of recommendations from tool results |
| `follow_up_at` | TIMESTAMP WITH TIME ZONE | Scheduled follow-up timestamp (optional) |
| `created_at` | TIMESTAMP WITH TIME ZONE | Creation timestamp |

**Indexes:**
- Primary key on `interaction_id`
- Foreign key to `users.user_id`

**`input` JSONB Structure:**
```json
{
  "text": "I have chest pain",
  "tools_called": ["triage_and_risk_flagging", "referrals_and_scheduling"]
}
```

**`triage_result` JSONB Structure (from structured JSON response):**
```json
{
  "status": "success",
  "risk_level": "high",
  "recommendation": "immediate clinical evaluation recommended",
  "symptoms": "chest pain for 2 hours",
  "urgency": "high",
  "patient_id": "uuid-here",
  "notes": "patient has history of heart disease"
}
```

**`recommendations` JSONB Structure:**
```json
["immediate clinical evaluation recommended"]
```

**Future Architectural Slot:**
- `tools` JSONB column: Full tool invocation details including name, args, and results
  ```json
  [
    {
      "name": "triage_and_risk_flagging",
      "args": {"symptoms": "...", "urgency": "high"},
      "result": {"status": "success", "risk_level": "high", ...}
    }
  ]
  ```
- This will enable complete audit trail, easier querying, and analytics

#### 3. `consents`

Stores user consent records for various scopes.

| Column | Type | Description |
|--------|------|-------------|
| `consent_id` | UUID | Primary key |
| `user_id` | UUID | Foreign key to `users.user_id` |
| `scope` | TEXT | Consent scope (e.g., `"data_sharing"`, `"treatment"`) |
| `status` | TEXT | Consent status (e.g., `"granted"`, `"revoked"`) |
| `version` | TEXT | Consent version identifier |
| `jurisdiction` | TEXT | Legal jurisdiction |
| `evidence` | JSONB | Consent evidence/record |
| `recorded_at` | TIMESTAMP WITH TIME ZONE | Consent recording timestamp |

**Indexes:**
- Primary key on `consent_id`
- Foreign key to `users.user_id`

#### 4. `providers`

Stores healthcare provider information for appointment scheduling.

| Column | Type | Description |
|--------|------|-------------|
| `provider_id` | UUID | Primary key |
| `external_provider_id` | TEXT | Provider ID in external system (architectural slot) |
| `external_system` | TEXT | External system name (e.g., `"epic"`, `"openmrs"`) |
| `name` | TEXT | Provider name |
| `specialty` | TEXT | Medical specialty (e.g., `"cardiology"`, `"general_practice"`) |
| `facility` | TEXT | Facility or clinic name |
| `available_days` | TEXT[] | Array of available days (e.g., `["monday", "friday"]`) |
| `country_context_id` | TEXT | Country context identifier (ISO 3166-1 alpha-2 code) |
| `contact_info` | JSONB | Contact information (phone, email, etc.) |
| `is_active` | BOOLEAN | Whether provider is currently active (default: true) |
| `created_at` | TIMESTAMP WITH TIME ZONE | Creation timestamp |

**Indexes:**
- Primary key on `provider_id`
- Foreign key references: `appointments.provider_id`

#### 5. `appointments`

Stores appointment records created by the referrals tool.

| Column | Type | Description |
|--------|------|-------------|
| `appointment_id` | UUID | Primary key |
| `external_appointment_id` | TEXT | Appointment ID in external system (architectural slot) |
| `external_system` | TEXT | External system name (e.g., `"epic"`, `"openmrs"`) |
| `user_id` | UUID | Foreign key to `users.user_id` |
| `provider_id` | UUID | Foreign key to `providers.provider_id` |
| `specialty` | TEXT | Medical specialty for appointment |
| `appointment_date` | DATE | Scheduled appointment date |
| `appointment_time` | TIME | Scheduled appointment time |
| `status` | TEXT | Appointment status (e.g., `"scheduled"`, `"confirmed"`, `"cancelled"`) |
| `reason` | TEXT | Reason for appointment/referral |
| `triage_interaction_id` | UUID | Foreign key to `interactions.interaction_id` (links to originating triage) |
| `consent_id` | UUID | Foreign key to `consents.consent_id` (links to consent record) |
| `sync_status` | TEXT | Sync status with external system (e.g., `"pending"`, `"synced"`, `"failed"`) |
| `last_synced_at` | TIMESTAMP WITH TIME ZONE | Last sync timestamp with external system |
| `created_at` | TIMESTAMP WITH TIME ZONE | Creation timestamp |

**Indexes:**
- Primary key on `appointment_id`
- Foreign key to `users.user_id`
- Foreign key to `providers.provider_id`
- Foreign key to `interactions.interaction_id`
- Foreign key to `consents.consent_id`

## Interaction Storage Architecture

### Automatic Storage

All interactions are automatically stored when `process_message()` is called:
1. Tool information is extracted from the message chain
2. Interaction record is created in `interactions` table
3. Tool metadata (names, results, risk levels) is stored

### Current Storage Pattern

**Tool Names:**
- Stored in `input.tools_called` as JSONB array
- Example: `["triage_and_risk_flagging", "commodity_orders_and_fulfillment"]`

**Tool Results:**
- Triage tool: Structured JSON stored in `triage_result` JSONB
- Other tools: Results extracted and stored in `recommendations` or parsed from tool messages
- Risk level extracted and stored in `risk_level` column

**Extraction Logic:**
- `extract_tool_info_from_messages()` processes the message chain
- Parses structured JSON responses (triage tool)
- Falls back to string parsing for backward compatibility
- Extracts protocol info, risk levels, and recommendations

### Future Storage Pattern

**Full Tool Invocation Details:**
- `tools` JSONB column will store complete tool invocation data
- Enables querying: `WHERE tools @> '[{"name": "triage_and_risk_flagging"}]'`
- Provides complete audit trail for debugging and analytics

## Query Examples

### Get User Interactions
```sql
SELECT interaction_id, channel, input, risk_level, recommendations, created_at
FROM interactions
WHERE user_id = 'user-uuid-here'
ORDER BY created_at DESC
LIMIT 10;
```

### Find Interactions with Triage
```sql
SELECT interaction_id, triage_result, risk_level
FROM interactions
WHERE protocol_invoked = 'triage'
ORDER BY created_at DESC;
```

### Find High-Risk Interactions
```sql
SELECT interaction_id, user_id, risk_level, recommendations, created_at
FROM interactions
WHERE risk_level IN ('high', 'critical')
ORDER BY created_at DESC;
```

### Get Tool Usage (Current)
```sql
SELECT interaction_id, input->>'tools_called' as tools
FROM interactions
WHERE input->'tools_called' IS NOT NULL;
```

### Get Tool Usage (Future - with tools column)
```sql
SELECT interaction_id, tools
FROM interactions
WHERE tools @> '[{"name": "triage_and_risk_flagging"}]';
```

### User History (Complete)
```sql
SELECT 
    u.user_id,
    u.email,
    u.phone_e164,
    COUNT(i.interaction_id) as interaction_count,
    MAX(i.created_at) as last_interaction
FROM users u
LEFT JOIN interactions i ON u.user_id = i.user_id
WHERE u.user_id = 'user-uuid-here'
GROUP BY u.user_id, u.email, u.phone_e164;
```

### Get User Appointments
```sql
SELECT 
    a.appointment_id,
    p.name as provider_name,
    p.specialty,
    p.facility,
    a.appointment_date,
    a.appointment_time,
    a.status,
    a.reason
FROM appointments a
LEFT JOIN providers p ON a.provider_id = p.provider_id
WHERE a.user_id = 'user-uuid-here'
ORDER BY a.appointment_date DESC, a.appointment_time DESC;
```

### Find Providers by Specialty
```sql
SELECT provider_id, name, specialty, facility, available_days
FROM providers
WHERE specialty = 'cardiology' 
AND is_active = true
AND country_context_id = 'us';
```

### Link Triage to Appointment
```sql
SELECT 
    i.interaction_id,
    i.risk_level,
    i.triage_result->>'symptoms' as symptoms,
    a.appointment_id,
    p.name as provider_name,
    a.appointment_date,
    c.status as consent_status
FROM interactions i
LEFT JOIN appointments a ON a.triage_interaction_id = i.interaction_id
LEFT JOIN providers p ON a.provider_id = p.provider_id
LEFT JOIN consents c ON a.consent_id = c.consent_id
WHERE i.user_id = 'user-uuid-here'
AND i.protocol_invoked = 'triage'
ORDER BY i.created_at DESC;
```

## Seed Files

Seed data is in `seeds/`:
- `demo.json` - all demo data (users, providers, appointments, consents, RAG documents)
- Add more seed files as needed (e.g., `production.json`, `test.json`)

See `docs/reference/seeds.md` for seed templates and structure.

## Database Access

### Command Line (psql)
```bash
# From host
psql postgresql://postgres:postgres@localhost:5432/selfcare

# From container
make shell-db
```

### pgAdmin Web Interface
- URL: `http://localhost:5050`
- Email: `admin@admin.com`
- Password: `admin`

### Python Connection
```python
from src.db import get_db_cursor

with get_db_cursor() as cur:
    cur.execute("SELECT * FROM users LIMIT 5")
    results = cur.fetchall()
```

## Schema Migration Notes

### Adding New Columns

1. Update `scripts/db/create_tables.py` with new column definition
2. Run `make create-tables` (uses `CREATE TABLE IF NOT EXISTS`, so existing tables won't be modified)
3. For existing databases, create migration script or manually add column:
   ```sql
   ALTER TABLE interactions ADD COLUMN IF NOT EXISTS tools JSONB;
   ```

### Future Schema Changes

When adding the `tools` JSONB column:
1. Add to `CREATE TABLE` statement in `create_tables.py`
2. Create migration script for existing databases
3. Update `save_interaction()` to populate the column
4. Update `extract_tool_info_from_messages()` to capture full tool details

## Best Practices

### Query Performance
- Use indexes on frequently queried columns (`user_id`, `created_at`)
- Use JSONB operators for efficient JSON queries (`@>`, `->`, `->>`)
- Consider materialized views for complex analytics queries

### Data Integrity
- Always use parameterized queries (via `get_db_cursor()`)
- Foreign key constraints ensure referential integrity
- Soft deletes (`is_deleted`) preserve data for audit trail

### Security
- Never expose database credentials in code
- Use environment variables for connection strings
- Tools automatically use current user context (no cross-user data access)
