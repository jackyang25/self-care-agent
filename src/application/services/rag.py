"""RAG utilities for document storage and retrieval."""

import os
import json
import uuid
from typing import List, Optional, Dict, Any
from openai import OpenAI
from src.infrastructure.postgres.repositories.documents import (
    insert_document,
    search_documents_by_embedding,
    delete_document as _delete_document,
)
from src.infrastructure.postgres.repositories.sources import insert_source
from src.shared.schemas.services import DocumentSearchResult

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_embedding(text: str) -> List[float]:
    """generate embedding for text using OpenAI."""
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return response.data[0].embedding


def store_source(
    source_id: str,
    name: str,
    source_type: str,
    country_context_id: Optional[str] = None,
    version: Optional[str] = None,
    url: Optional[str] = None,
    publisher: Optional[str] = None,
    effective_date: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """store a source record in the database.

    args:
        source_id: unique identifier for the source
        name: source name (e.g., "APC 2023 Clinical Tool")
        source_type: type classification (e.g., "clinical_guideline", "protocol")
        country_context_id: country code or None for global
        version: version string
        url: original source URL
        publisher: publishing organization
        effective_date: date source became effective
        metadata: additional metadata

    returns:
        source_id if successful
    """
    metadata_json = json.dumps(metadata) if metadata else None

    insert_source(
        source_id=source_id,
        name=name,
        source_type=source_type,
        country_context_id=country_context_id,
        version=version,
        url=url,
        publisher=publisher,
        effective_date=effective_date,
        metadata_json=metadata_json,
    )

    return source_id


def store_document(
    title: str,
    content: str,
    content_type: str,
    source_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    section_path: Optional[List[str]] = None,
    country_context_id: Optional[str] = None,
    conditions: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """store a document with embedding in the database.

    args:
        title: document title
        content: document text content
        content_type: type classification (e.g., "symptom", "protocol", "guideline")
        source_id: optional reference to source
        parent_id: optional reference to parent document
        section_path: hierarchical path (e.g., ["Symptoms", "Fever", "Red Flags"])
        country_context_id: country code or None for global
        conditions: list of medical conditions this covers
        metadata: additional metadata

    returns:
        document_id
    """
    embedding = get_embedding(content)

    # convert metadata dict to json string for jsonb column
    metadata_json = json.dumps(metadata) if metadata else None

    document_id = str(uuid.uuid4())
    insert_document(
        document_id=document_id,
        title=title,
        content=content,
        content_type=content_type,
        embedding=embedding,
        source_id=source_id,
        parent_id=parent_id,
        section_path=section_path,
        country_context_id=country_context_id,
        conditions=conditions,
        metadata_json=metadata_json,
    )

    return document_id


def search_documents(
    query: str,
    limit: int = 5,
    content_type: Optional[str] = None,
    content_types: Optional[List[str]] = None,
    country_context_id: Optional[str] = None,
    conditions: Optional[List[str]] = None,
    min_similarity: float = 0.5,
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
        content_type: optional filter by single content type (deprecated)
        content_types: optional filter by multiple content types
        country_context_id: filter by country (includes global if include_global=True)
        conditions: optional filter by medical conditions
        min_similarity: minimum similarity score (0.0-1.0, default 0.5)
        include_global: whether to include documents with no country context

    returns:
        list of document dicts with title, content, similarity, source info, etc.
    """
    query_embedding = get_embedding(query)

    results = search_documents_by_embedding(
        query_embedding=query_embedding,
        limit=limit,
        content_type=content_type,
        content_types=content_types,
        country_context_id=country_context_id,
        conditions=conditions,
        include_global=include_global,
    )

    # apply minimum similarity threshold as quality gate and convert to Pydantic models
    filtered_results = []
    for doc in results:
        if doc["similarity"] >= min_similarity:
            filtered_results.append(DocumentSearchResult(
                title=doc["title"],
                content=doc["content"],
                similarity=doc["similarity"],
                source_name=doc.get("source_name"),
                source_version=doc.get("source_version"),
                content_type=doc.get("content_type"),
                country_context_id=doc.get("country_context_id"),
                conditions=doc.get("conditions"),
            ))
    
    return filtered_results


def delete_document(document_id: str) -> bool:
    """delete a document by ID."""
    return _delete_document(document_id)
