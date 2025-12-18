"""document data access functions for RAG."""

from typing import List, Optional, Dict, Any
from src.db import get_db_cursor


def insert_document(
    document_id: str,
    title: str,
    content: str,
    embedding: List[float],
    content_type: Optional[str] = None,
    metadata_json: Optional[str] = None,
) -> bool:
    """insert a document with embedding into database.

    args:
        document_id: unique document id
        title: document title
        content: document content
        embedding: vector embedding
        content_type: optional content type classification
        metadata_json: optional metadata as json string

    returns:
        True if successful, False otherwise
    """
    try:
        with get_db_cursor() as cur:
            cur.execute(
                """
                INSERT INTO documents (document_id, title, content, content_type, metadata, embedding)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s::vector)
                """,
                (document_id, title, content, content_type, metadata_json, embedding),
            )
            return True
    except Exception:
        return False


def search_documents_by_embedding(
    query_embedding: List[float],
    limit: int = 5,
    content_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """search for similar documents using vector similarity.

    args:
        query_embedding: query vector embedding
        limit: maximum number of results
        content_type: optional filter by content type

    returns:
        list of document dicts with similarity scores
    """
    try:
        with get_db_cursor() as cur:
            if content_type:
                cur.execute(
                    """
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
                    """,
                    (query_embedding, content_type, query_embedding, limit),
                )
            else:
                cur.execute(
                    """
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
                    """,
                    (query_embedding, query_embedding, limit),
                )

            results = []
            for row in cur.fetchall():
                results.append(
                    {
                        "document_id": str(row["document_id"]),
                        "title": row["title"],
                        "content": row["content"],
                        "content_type": row["content_type"],
                        "metadata": row["metadata"],
                        "similarity": float(row["similarity"]),
                    }
                )
            return results
    except Exception:
        return []


def delete_document(document_id: str) -> bool:
    """delete a document by ID.

    args:
        document_id: document uuid

    returns:
        True if document was deleted, False otherwise
    """
    try:
        with get_db_cursor() as cur:
            cur.execute("DELETE FROM documents WHERE document_id = %s", (document_id,))
            return cur.rowcount > 0
    except Exception:
        return False


def get_document_by_id(document_id: str) -> Optional[Dict[str, Any]]:
    """get document by document_id.

    args:
        document_id: document uuid

    returns:
        document dict or None if not found
    """
    try:
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT 
                    document_id,
                    title,
                    content,
                    content_type,
                    metadata
                FROM documents
                WHERE document_id = %s
                """,
                (document_id,),
            )
            result = cur.fetchone()
            if result:
                return {
                    "document_id": str(result["document_id"]),
                    "title": result["title"],
                    "content": result["content"],
                    "content_type": result["content_type"],
                    "metadata": result["metadata"],
                }
            return None
    except Exception:
        return None
