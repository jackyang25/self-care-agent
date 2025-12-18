"""RAG utilities for document storage and retrieval."""

import os
import json
import uuid
from typing import List, Optional, Dict, Any
from openai import OpenAI
from src.data.documents import (
    insert_document,
    search_documents_by_embedding,
    delete_document as _delete_document,
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_embedding(text: str) -> List[float]:
    """generate embedding for text using OpenAI."""
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return response.data[0].embedding


def store_document(
    title: str,
    content: str,
    content_type: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """store a document with embedding in the database."""
    embedding = get_embedding(content)

    # convert metadata dict to json string for jsonb column
    metadata_json = json.dumps(metadata) if metadata else None

    document_id = str(uuid.uuid4())
    insert_document(
        document_id=document_id,
        title=title,
        content=content,
        embedding=embedding,
        content_type=content_type,
        metadata_json=metadata_json,
    )

    return document_id


def search_documents(
    query: str,
    limit: int = 5,
    content_type: Optional[str] = None,
    min_similarity: float = 0.5,
) -> List[Dict[str, Any]]:
    """search for similar documents using vector similarity.

    uses top-k approach with minimum similarity threshold:
    - returns top 'limit' most similar documents
    - filters out results below min_similarity (quality gate)
    - ensures results when relevant documents exist

    args:
        query: search query text
        limit: maximum number of documents to return (top-k)
        content_type: optional filter by content type
        min_similarity: minimum similarity score (0.0-1.0, default 0.5)

    returns:
        list of document dicts with title, content, similarity, etc.
    """
    query_embedding = get_embedding(query)

    results = search_documents_by_embedding(
        query_embedding=query_embedding,
        limit=limit,
        content_type=content_type,
    )

    # apply minimum similarity threshold as quality gate
    filtered_results = [doc for doc in results if doc["similarity"] >= min_similarity]

    return filtered_results


def delete_document(document_id: str) -> bool:
    """delete a document by ID."""
    return _delete_document(document_id)
