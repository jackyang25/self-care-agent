"""RAG utilities for document storage and retrieval."""

from typing import List, Optional
from openai import OpenAI
from src.infrastructure.postgres.repositories.documents import (
    search_documents_by_embedding,
)
from src.application.services.schemas.rag import DocumentSearchResult
from src.shared.config import (
    EMBEDDING_MODEL,
    OPENAI_API_KEY,
    RAG_LIMIT_DEFAULT,
    RAG_MIN_SIMILARITY,
)

client = OpenAI(api_key=OPENAI_API_KEY)


def get_embedding(text: str) -> List[float]:
    """generate embedding for text using OpenAI."""
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding


def search_documents(
    query: str,
    limit: int = RAG_LIMIT_DEFAULT,
    content_types: Optional[List[str]] = None,
    country_context_id: Optional[str] = None,
    conditions: Optional[List[str]] = None,
    min_similarity: float = RAG_MIN_SIMILARITY,
    include_global: bool = True,
) -> List[DocumentSearchResult]:
    """search for similar documents using vector similarity.

    uses top-k approach with filtering and minimum similarity threshold:
    - filters by country context (user's country + global docs)
    - filters by content type(s) if specified
    - filters by medical conditions if specified
    - returns top 'limit' most similar documents
    - filters out results below min_similarity (quality gate)

    args:
        query: search query text
        limit: maximum number of documents to return (top-k)
        content_types: optional filter by multiple content types
        country_context_id: filter by country (includes global if include_global=True)
        conditions: optional filter by medical conditions
        min_similarity: minimum similarity score (0.0-1.0, default 0.35)
        include_global: whether to include documents with no country context

    returns:
        list of document dicts with title, content, similarity, source info, etc.
    """
    query_embedding = get_embedding(query)

    results = search_documents_by_embedding(
        query_embedding=query_embedding,
        limit=limit,
        content_types=content_types,
        country_context_id=country_context_id,
        conditions=conditions,
        include_global=include_global,
    )

    # apply minimum similarity threshold as quality gate and convert to Pydantic models
    filtered_results = []
    for doc in results:
        if doc["similarity"] >= min_similarity:
            filtered_results.append(
                DocumentSearchResult(
                    title=doc["title"],
                    content=doc["content"],
                    similarity=doc["similarity"],
                    source_name=doc.get("source_name"),
                    source_version=doc.get("source_version"),
                    content_type=doc.get("content_type"),
                    country_context_id=doc.get("country_context_id"),
                    conditions=doc.get("conditions"),
                )
            )

    return filtered_results
