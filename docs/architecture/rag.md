# RAG (Retrieval-Augmented Generation) Implementation

## Overview

RAG (Retrieval-Augmented Generation) enhances the agent's responses by retrieving relevant information from a healthcare knowledge base. This implementation uses PostgreSQL with `pgvector` for vector similarity search, supporting **country-specific clinical guidelines** alongside global content.

## Architecture

### Components

1. **pgvector Extension**: Vector similarity search in PostgreSQL
2. **Sources Table**: Tracks document provenance (where content came from)
3. **Documents Table**: Healthcare knowledge with embeddings and rich metadata
4. **Embedding Model**: OpenAI's `text-embedding-3-small` (1536 dimensions)
5. **RAG Tool**: LangChain tool with country-aware retrieval

### How It Works

```
User Query (e.g., "How do I manage fever?")
    │
    ▼
┌─────────────────────────────────────────┐
│  1. Get user's country_context_id       │
│     (e.g., "za" for South Africa)       │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  2. Convert query to embedding          │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  3. Vector search with filters:         │
│     - country = "za" OR country IS NULL │
│     - content_type (optional)           │
│     - conditions (optional)             │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  4. Return ranked documents with        │
│     source attribution                  │
└─────────────────────────────────────────┘
    │
    ▼
Agent uses context to generate response
```

## Database Schema

### `sources` Table

Tracks where documents come from for provenance and versioning.

| Column | Type | Description |
|--------|------|-------------|
| `source_id` | UUID | Primary key |
| `name` | TEXT | Source name (e.g., "APC 2023 Clinical Tool") |
| `source_type` | TEXT | Type: "clinical_guideline", "protocol", "guideline" |
| `country_context_id` | TEXT | Country code (e.g., "za", "ke") or NULL for global |
| `version` | TEXT | Version string (e.g., "2023", "v3.1") |
| `url` | TEXT | Original source URL |
| `publisher` | TEXT | Publishing organization |
| `effective_date` | DATE | When source became effective |
| `metadata` | JSONB | Additional metadata |
| `created_at` | TIMESTAMP | Creation timestamp |

### `documents` Table

Stores document chunks with embeddings and rich metadata for filtering.

| Column | Type | Description |
|--------|------|-------------|
| `document_id` | UUID | Primary key |
| `source_id` | UUID | Foreign key to sources (provenance) |
| `parent_id` | UUID | Self-reference for chunked documents |
| `title` | TEXT | Document title |
| `content` | TEXT | Full document text |
| `content_type` | TEXT | Type classification (see taxonomy below) |
| `section_path` | TEXT[] | Hierarchical path (e.g., `["Symptoms", "Fever", "Red Flags"]`) |
| `country_context_id` | TEXT | Country code or NULL for global |
| `conditions` | TEXT[] | Medical conditions covered (e.g., `["fever", "malaria"]`) |
| `embedding` | vector(1536) | Vector embedding |
| `metadata` | JSONB | Additional metadata |
| `created_at` | TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

**Indexes:**
- Vector similarity index on `embedding` (IVFFlat with cosine distance)
- `content_type` index for filtering
- `country_context_id` index for country filtering
- GIN index on `conditions` for array search
- GIN index on `section_path` for hierarchy search

## Content Type Taxonomy

```
content_type:
├── symptom          # Entry points for symptom-based triage
├── condition        # Chronic condition information
├── algorithm        # Clinical decision trees/flowcharts
├── protocol         # Step-by-step clinical protocols
├── guideline        # General management guidance
├── medication       # Drug info, dosing, prescriber levels
├── reference        # Helplines, tables, quick reference
└── emergency        # Red flags, urgent care criteria
```

## Country-Aware Retrieval

The RAG system automatically prioritizes country-specific content:

1. **User context**: `country_context_id` is set from the user's profile
2. **Query filtering**: Search includes documents where:
   - `country_context_id` matches user's country, OR
   - `country_context_id` IS NULL (global content)
3. **Ranking**: Vector similarity determines relevance within filtered set

**Example**: A user in South Africa asking about TB gets:
- SA-specific "TB Screening Algorithm (South Africa)" from APC 2023
- Global "Tuberculosis (TB) Screening and Testing" as backup

## Setup

### 1. Install Dependencies

Already in `requirements.txt`:
- `pgvector>=0.2.0`
- `numpy>=1.24.0`

### 2. Create Tables

```bash
make create-tables
```

This creates:
- `sources` table for document provenance
- Enhanced `documents` table with all indexes

### 3. Seed Data

```bash
make seed-db
```

Seeds from `seeds/demo.json`:
- 2 sources (Global Guidelines, APC 2023 for SA)
- 18 documents with country context and conditions

## Usage

### Adding a New Source

```python
from src.services.rag import store_source

store_source(
    source_id="uuid-here",
    name="Kenya Clinical Guidelines 2024",
    source_type="clinical_guideline",
    country_context_id="ke",
    version="2024",
    url="https://example.com/kenya-guidelines.pdf",
    publisher="Kenya Ministry of Health",
    effective_date="2024-01-01",
)
```

### Adding Documents

```python
from src.services.rag import store_document

document_id = store_document(
    title="Fever Management (Kenya)",
    content="...",
    content_type="guideline",
    source_id="source-uuid",  # Link to source
    section_path=["Symptoms", "Fever"],
    country_context_id="ke",
    conditions=["fever", "malaria"],
    metadata={"page_ref": "23"},
)
```

### Searching Documents

```python
from src.services.rag import search_documents

# Country-aware search (includes global + country-specific)
results = search_documents(
    query="fever treatment red flags",
    country_context_id="za",
    content_types=["guideline", "emergency"],
    conditions=["fever"],
    limit=5,
    min_similarity=0.5,
)
```

## RAG Tool

**Tool Name:** `rag_retrieval`

**Parameters:**
- `query` (required): Search query text
- `content_type` (optional): Single content type filter
- `content_types` (optional): Multiple content types
- `conditions` (optional): Medical conditions to filter by
- `limit` (optional, default: 5): Max documents to retrieve

**Automatic Context:**
- User's `country_context_id` is automatically applied from session

**Returns:**
```json
{
  "status": "success",
  "query": "fever management",
  "results_count": 3,
  "documents": [
    {
      "title": "Fever - Red Flags (South Africa)",
      "content": "...",
      "content_type": "emergency",
      "similarity": 0.87,
      "source": "Adult Primary Care 2023 (2023)",
      "country": "za",
      "conditions": ["fever", "malaria"]
    }
  ]
}
```

## Best Practices

### Document Content
- **Chunk size**: 500-1500 tokens per document
- **One concept per chunk**: Don't mix unrelated content
- **Clear structure**: Use section_path for navigation

### Seed Data Structure
```json
{
  "sources": [
    {
      "source_id": "uuid",
      "name": "Source Name",
      "source_type": "clinical_guideline",
      "country_context_id": "za",
      "version": "2023"
    }
  ],
  "documents": [
    {
      "title": "Document Title",
      "content": "...",
      "content_type": "protocol",
      "source_id": "uuid",
      "section_path": ["Section", "Subsection"],
      "country_context_id": "za",
      "conditions": ["condition1", "condition2"]
    }
  ]
}
```

### Content Type Selection

| Use Case | Recommended content_types |
|----------|--------------------------|
| Emergency/urgent symptoms | `["emergency"]` |
| General health questions | `["guideline", "protocol"]` |
| Chronic disease management | `["condition", "guideline"]` |
| Clinical decision support | `["algorithm", "protocol"]` |
| Drug information | `["medication"]` |
| Helplines/contacts | `["reference"]` |

## Troubleshooting

### No Country-Specific Results
- Verify documents have `country_context_id` set
- Check user's `country_context_id` in session
- Global docs (NULL country) are always included as fallback

### Low Similarity Scores
- Default threshold is 0.5 (50%)
- Lower threshold for broader results
- Check query specificity

### Missing Source Information
- Ensure `source_id` is set when storing documents
- Sources must be seeded before documents that reference them

## Future Enhancements

1. **Automated Ingestion Pipeline**: PDF → Markdown → Chunks → Embeddings
2. **Hybrid Search**: Combine vector + keyword search
3. **Cross-Encoder Re-ranking**: Improve result ordering
4. **Multi-language Support**: Embeddings for local languages
5. **Document Versioning**: Track updates to clinical guidelines
