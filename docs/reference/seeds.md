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
  "sources": [...],
  "documents": [...]
}
```

**Note:** Sources must be seeded before documents that reference them.

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

### Sources Template (RAG)
```json
{
  "source_id": "uuid (required)",
  "name": "Adult Primary Care 2023",
  "source_type": "clinical_guideline|protocol|guideline",
  "country_context_id": "za|ke|us|... or null for global",
  "version": "2023",
  "url": "https://example.com/guidelines.pdf",
  "publisher": "National Department of Health",
  "effective_date": "2023-10-01",
  "metadata": {
    "description": "Comprehensive clinical tool for adult primary care"
  }
}
```

### Documents Template (RAG)
```json
{
  "title": "Fever - Red Flags (South Africa)",
  "content": "Full document text content...",
  "content_type": "symptom|condition|algorithm|protocol|guideline|medication|reference|emergency",
  "source_id": "uuid (optional, reference to sources)",
  "section_path": ["Symptoms", "Fever", "Red Flags"],
  "country_context_id": "za|ke|us|... or null for global",
  "conditions": ["fever", "malaria"],
  "metadata": {
    "category": "emergency",
    "page_ref": "23"
  }
}
```

### Content Type Reference

| content_type | Description | When to use |
|--------------|-------------|-------------|
| `symptom` | Entry points for symptom-based triage | Initial symptom assessment |
| `condition` | Chronic condition information | Disease-specific guidance |
| `algorithm` | Clinical decision trees/flowcharts | Structured clinical decisions |
| `protocol` | Step-by-step clinical protocols | Treatment procedures |
| `guideline` | General management guidance | General health advice |
| `medication` | Drug info, dosing, prescriber levels | Medication information |
| `reference` | Helplines, tables, quick reference | Contact info, lookup tables |
| `emergency` | Red flags, urgent care criteria | Emergency/urgent situations |

