# Seeds

Seed data files for seeding the database are located in `seeds/` (at the project root). This document describes their structure and usage.

## Seed Files vs Templates

- **Seed files** (e.g., `demo.json`) = actual data that gets loaded into the database
- **Templates** (below) = structure examples for reference when creating new seed files

## Structure

Seed files should be JSON files with the following structure:

```json
{
  "users": [...],
  "interactions": [...],
  "consents": [...],
  "providers": [...],
  "appointments": [...],
  "documents": [...]
}
```

## Available Seed Files

- `demo.json` - all demo data (users, interactions, providers, appointments, consents, RAG documents)

You can create additional seed files (e.g., `test.json`, `production.json`) following the same structure.

## Usage

Seed all data (app + RAG):
```bash
python scripts/db/seed.py
```

Seed a specific table:
```bash
python scripts/db/seed.py --table users
```

Clear existing data before seeding:
```bash
python scripts/db/seed.py --clear
```

Use a different seed file:
```bash
python scripts/db/seed.py --file test.json
```

Or use the Makefile:
```bash
make seed-db
```

## Data Structure Templates

Use these templates as a reference when creating new seed files. The templates show the expected structure and field types.

### Users Template
```json
{
  "user_id": "uuid (optional, auto-generated if not provided)",
  "fhir_patient_id": "string",
  "primary_channel": "whatsapp|sms|voice",
  "phone_e164": "+1234567890",
  "email": "user@example.com",
  "preferred_language": "en|es|fr|...",
  "literacy_mode": "standard|simplified",
  "country_context_id": "us|mx|ke|... (ISO 3166-1 alpha-2 country code)",
  "demographics": {
    "age": 35,
    "gender": "male|female|other"
  },
  "accessibility": {
    "hearing_aid": false,
    "visual_aid": false
  }
}
```

### Interactions Template
```json
{
  "interaction_id": "uuid (optional)",
  "user_id": "uuid (required)",
  "channel": "whatsapp|sms|voice",
  "input": "user input text",
  "protocol_invoked": "triage|pharmacy|referral|commodity",
  "protocol_version": "1.0",
  "triage_result": {
    "risk_level": "low|medium|high",
    "symptoms": ["symptom1", "symptom2"]
  },
  "risk_level": "low|medium|high",
  "recommendations": ["recommendation1", "recommendation2"],
  "follow_up_at": "2024-01-01T00:00:00Z or null"
}
```

### Consents Template
```json
{
  "consent_id": "uuid (optional)",
  "user_id": "uuid (required)",
  "scope": "triage|pharmacy|referral|commodity",
  "status": "granted|denied|revoked",
  "version": "1.0",
  "jurisdiction": "us|mx|...",
  "evidence": {
    "method": "explicit|implicit",
    "timestamp": "2024-01-01T00:00:00Z"
  },
  "recorded_at": "2024-01-01T00:00:00Z"
}
```

### Providers Template
```json
{
  "provider_id": "uuid (optional)",
  "external_provider_id": "string (optional)",
  "external_system": "epic|openmrs|cerner|...",
  "name": "Dr. Jane Smith",
  "specialty": "cardiology|pediatrics|general_practice|...",
  "facility": "Main Hospital",
  "available_days": ["monday", "wednesday", "friday"],
  "country_context_id": "us|mx|ke|... (ISO 3166-1 alpha-2)",
  "contact_info": {
    "phone": "+1234567890",
    "email": "provider@example.com"
  },
  "is_active": true
}
```

### Appointments Template
```json
{
  "appointment_id": "uuid (optional)",
  "external_appointment_id": "string (optional)",
  "external_system": "epic|openmrs|cerner|...",
  "user_id": "uuid (required)",
  "provider_id": "uuid (required)",
  "specialty": "cardiology|pediatrics|...",
  "appointment_date": "2024-12-25",
  "appointment_time": "10:00:00",
  "status": "scheduled|confirmed|cancelled|completed",
  "reason": "Follow-up for chest pain",
  "triage_interaction_id": "uuid (optional)",
  "consent_id": "uuid (optional)",
  "sync_status": "pending|synced|failed",
  "last_synced_at": "2024-01-01T00:00:00Z or null"
}
```

### Documents Template (RAG)
```json
{
  "document_id": "uuid (optional)",
  "title": "Fever Management Guidelines",
  "content": "Full document text content...",
  "content_type": "protocol|guideline|reference|...",
  "metadata": {
    "category": "symptom_management",
    "condition": "fever",
    "source": "WHO Guidelines 2024"
  }
}
```

