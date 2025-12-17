# RAG (Retrieval-Augmented Generation) Implementation

## Overview

RAG (Retrieval-Augmented Generation) is an AI pattern that enhances the agent's responses by retrieving relevant information from a knowledge base. This implementation uses PostgreSQL with the `pgvector` extension for vector similarity search.

## Architecture

### Components

1. **pgvector Extension**: Enables vector similarity search in PostgreSQL
2. **Documents Table**: Stores healthcare knowledge base content with embeddings
3. **Embedding Model**: OpenAI's `text-embedding-3-small` (1536 dimensions)
4. **RAG Tool**: LangChain tool that retrieves relevant documents for the agent

### How It Works

1. Documents are stored with their text embeddings (vector representations)
2. User queries are converted to embeddings
3. Vector similarity search finds the most relevant documents
4. Retrieved documents are provided to the agent as context
5. Agent uses this context to generate informed responses

## Setup

### 1. Install Dependencies

Dependencies are already added to `requirements.txt`:
- `pgvector>=0.2.0` - PostgreSQL vector extension support
- `numpy>=1.24.0` - Required for vector operations

### 2. Update Docker Image

The `docker-compose.yml` has been updated to use `pgvector/pgvector:pg15` image which includes the pgvector extension.

### 3. Create RAG Tables

```bash
make create-rag-tables
```

This will:
- Enable the `vector` extension in PostgreSQL
- Create the `documents` table
- Create vector similarity indexes for efficient search

### 4. Seed Sample Documents (Optional)

```bash
make seed-rag
```

This seeds 5 sample healthcare documents covering:
- Fever management
- Chest pain red flags
- Diabetes self-care
- Hypertension management
- Emergency care guidelines

## Database Schema

### `documents` Table

| Column | Type | Description |
|--------|------|-------------|
| `document_id` | UUID | Primary key |
| `title` | TEXT | Document title |
| `content` | TEXT | Full document text |
| `content_type` | TEXT | Type/category (e.g., "protocol", "guideline") |
| `metadata` | JSONB | Additional metadata (flexible structure) |
| `embedding` | vector(1536) | Vector embedding of content |
| `created_at` | TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

**Indexes:**
- Vector similarity index on `embedding` (IVFFlat with cosine distance)
- Content type index for filtering

## Usage

### Adding Documents

Use the `store_document()` function from `src/utils/rag.py`:

```python
from src.utils.rag import store_document

document_id = store_document(
    title="Diabetes Management Guidelines",
    content="...",
    content_type="guideline",
    metadata={"category": "chronic_disease", "condition": "diabetes"}
)
```

### Searching Documents

The RAG tool is automatically available to the agent. The agent will call it when:
- User asks questions about symptoms, conditions, or treatments
- Agent needs evidence-based information
- User requests information about health topics

**Example Agent Usage:**
```
User: "What should I know about diabetes?"
  ↓
Agent → rag_retrieval(query="diabetes management and self-care")
  ↓
Agent → Response with retrieved information
```

### Manual Search (Python)

```python
from src.utils.rag import search_documents

results = search_documents(
    query="fever treatment",
    limit=3,
    content_type="guideline",
    similarity_threshold=0.7
)
```

## RAG Tool

**Tool Name:** `rag_retrieval`

**Parameters:**
- `query` (required): Search query text
- `content_type` (optional): Filter by content type
- `limit` (optional, default: 3): Maximum documents to retrieve

**Returns:**
- Formatted JSON with document titles, content, and similarity scores

**When Agent Uses It:**
- User asks health-related questions
- Agent needs authoritative healthcare knowledge
- User requests information about symptoms, conditions, or treatments

## Best Practices

### Document Content

- **Chunk Size**: Keep documents focused (500-2000 words recommended)
- **Clarity**: Write clear, structured content
- **Metadata**: Use consistent content_type values and meaningful metadata
- **Updates**: When updating documents, regenerate embeddings

### Query Optimization

- **Specificity**: More specific queries yield better results
- **Context**: Include relevant context in queries (e.g., "adult fever management" vs "fever")
- **Filtering**: Use content_type filtering when appropriate

### Similarity Threshold

- Default: 0.7 (70% similarity)
- Adjust based on your needs:
  - Higher (0.8-0.9): More strict, fewer but highly relevant results
  - Lower (0.5-0.6): More lenient, more results but potentially less relevant

## Integration with Agent

The RAG tool is automatically registered in `src/tools/__init__.py` and available to the agent. The agent's system prompt should guide when to use RAG vs. other tools:

- **RAG**: For general health knowledge, protocols, guidelines
- **Triage Tool**: For user-specific symptom assessment
- **Database Tool**: For user-specific data retrieval

## Troubleshooting

### pgvector Extension Not Found

If you see errors about the vector type:
1. Ensure you're using `pgvector/pgvector:pg15` image
2. Run `make create-rag-tables` to enable the extension

### No Results Returned

- Check that documents exist: `SELECT COUNT(*) FROM documents;`
- Lower the similarity threshold
- Verify embeddings were generated (check `embedding IS NOT NULL`)

### Slow Queries

- Ensure vector index exists: `\d documents` in psql
- Consider adjusting IVFFlat lists parameter for larger datasets
- Use content_type filtering to narrow search space

## Future Enhancements

Potential improvements:
- **Chunking**: Split large documents into smaller chunks for better retrieval
- **Hybrid Search**: Combine vector search with keyword search
- **Re-ranking**: Use cross-encoder models to re-rank results
- **Metadata Filtering**: More sophisticated filtering by metadata fields
- **Update Pipeline**: Automated document update and re-embedding process

