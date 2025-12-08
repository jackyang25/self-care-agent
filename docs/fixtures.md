# Fixtures

Fixture data files for seeding the database are located in `fixtures/` (at the project root). This document describes their structure and usage.

## Fixture Files vs Templates

- **Fixture files** (e.g., `seed_data.json`) = actual data that gets loaded into the database
- **Templates** (below) = structure examples for reference when creating new fixtures

## Structure

Fixture files should be JSON files with the following structure:

```json
{
  "users": [...],
  "interactions": [...],
  "consents": [...]
}
```

## Available Fixtures

- `seed_data.json` - default seed data with example users, interactions, and consents

You can create additional fixture files (e.g., `test_data.json`, `demo_data.json`) following the same structure.

## Usage

Seed all tables from `seed_data.json`:
```bash
python scripts/seed_db.py
```

Seed a specific table:
```bash
python scripts/seed_db.py --table users
```

Clear existing data before seeding:
```bash
python scripts/seed_db.py --clear
```

Use a different fixture file:
```bash
python scripts/seed_db.py --file test_data.json
```

Or use the Makefile:
```bash
make seed-db
```

## Data Structure Templates

Use these templates as a reference when creating new fixture files. The templates show the expected structure and field types.

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
  "country_context_id": "us|mx|...",
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

