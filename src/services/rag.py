"""RAG utilities for document storage and retrieval."""

import os
import json
import uuid
from typing import List, Optional, Dict, Any
from openai import OpenAI
from src.db import get_db_cursor

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_embedding(text: str) -> List[float]:
    """generate embedding for text using OpenAI."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
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
    
    with get_db_cursor() as cur:
        document_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO documents (document_id, title, content, content_type, metadata, embedding)
            VALUES (%s, %s, %s, %s, %s::jsonb, %s::vector)
        """, (document_id, title, content, content_type, metadata_json, embedding))
    
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
    
    with get_db_cursor() as cur:
        if content_type:
            cur.execute("""
                SELECT 
                    document_id,
                    title,
                    content,
                    content_type,
                    metadata,
                    1 - (embedding <=> %s::vector) as similarity
                FROM documents
                WHERE content_type = %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (query_embedding, content_type, query_embedding, limit))
        else:
            cur.execute("""
                SELECT 
                    document_id,
                    title,
                    content,
                    content_type,
                    metadata,
                    1 - (embedding <=> %s::vector) as similarity
                FROM documents
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (query_embedding, query_embedding, limit))
        
        results = []
        for row in cur.fetchall():
            similarity = float(row["similarity"])
            # apply minimum similarity threshold as quality gate
            if similarity >= min_similarity:
                results.append({
                    "document_id": str(row["document_id"]),
                    "title": row["title"],
                    "content": row["content"],
                    "content_type": row["content_type"],
                    "metadata": row["metadata"],
                    "similarity": similarity,
                })
    
    return results


def delete_document(document_id: str) -> bool:
    """delete a document by ID."""
    with get_db_cursor() as cur:
        cur.execute("DELETE FROM documents WHERE document_id = %s", (document_id,))
        return cur.rowcount > 0

