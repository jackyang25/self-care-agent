"""document data access functions for RAG."""

from typing import List, Optional, Dict, Any
from src.db import get_db_cursor


def insert_document(
    document_id: str,
    title: str,
    content: str,
    content_type: str,
    embedding: List[float],
    source_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    section_path: Optional[List[str]] = None,
    country_context_id: Optional[str] = None,
    conditions: Optional[List[str]] = None,
    metadata_json: Optional[str] = None,
) -> bool:
    """insert a document with embedding into database.

    args:
        document_id: unique document id
        title: document title
        content: document content
        content_type: content type classification (required)
        embedding: vector embedding
        source_id: optional reference to source document
        parent_id: optional reference to parent document (for chunked docs)
        section_path: hierarchical path (e.g., ["Symptoms", "Fever", "Red Flags"])
        country_context_id: country code (e.g., "za", "ke") or None for global
        conditions: list of medical conditions this document covers
        metadata_json: optional metadata as json string

    returns:
        True if successful, False otherwise
    """
    try:
        with get_db_cursor() as cur:
            cur.execute(
                """
                INSERT INTO documents (
                    document_id, source_id, parent_id, title, content, content_type,
                    section_path, country_context_id, conditions, embedding, metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::vector, %s::jsonb)
                ON CONFLICT (document_id) DO UPDATE SET
                    source_id = EXCLUDED.source_id,
                    parent_id = EXCLUDED.parent_id,
                    title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    content_type = EXCLUDED.content_type,
                    section_path = EXCLUDED.section_path,
                    country_context_id = EXCLUDED.country_context_id,
                    conditions = EXCLUDED.conditions,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    updated_at = now()
                """,
                (
                    document_id,
                    source_id,
                    parent_id,
                    title,
                    content,
                    content_type,
                    section_path,
                    country_context_id,
                    conditions,
                    embedding,
                    metadata_json,
                ),
            )
            return True
    except Exception:
        return False


def search_documents_by_embedding(
    query_embedding: List[float],
    limit: int = 5,
    content_type: Optional[str] = None,
    content_types: Optional[List[str]] = None,
    country_context_id: Optional[str] = None,
    conditions: Optional[List[str]] = None,
    include_global: bool = True,
) -> List[Dict[str, Any]]:
    """search for similar documents using vector similarity with filtering.

    args:
        query_embedding: query vector embedding
        limit: maximum number of results
        content_type: optional filter by single content type (deprecated, use content_types)
        content_types: optional filter by multiple content types
        country_context_id: optional filter by country (includes global docs if include_global=True)
        conditions: optional filter by medical conditions (matches any)
        include_global: whether to include global docs (country_context_id IS NULL)

    returns:
        list of document dicts with similarity scores
    """
    try:
        with get_db_cursor() as cur:
            # build dynamic WHERE clause
            where_clauses = []
            params = [query_embedding]

            # handle content type filtering
            if content_types:
                where_clauses.append("content_type = ANY(%s)")
                params.append(content_types)
            elif content_type:
                where_clauses.append("content_type = %s")
                params.append(content_type)

            # handle country filtering
            if country_context_id:
                if include_global:
                    where_clauses.append("(country_context_id = %s OR country_context_id IS NULL)")
                else:
                    where_clauses.append("country_context_id = %s")
                params.append(country_context_id)

            # handle conditions filtering (matches any condition in the list)
            if conditions:
                where_clauses.append("conditions && %s")
                params.append(conditions)

            # construct query
            where_sql = ""
            if where_clauses:
                where_sql = "WHERE " + " AND ".join(where_clauses)

            # add embedding for ORDER BY
            params.append(query_embedding)
            params.append(limit)

            query = f"""
                SELECT 
                    d.document_id,
                    d.title,
                    d.content,
                    d.content_type,
                    d.section_path,
                    d.country_context_id,
                    d.conditions,
                    d.metadata,
                    d.source_id,
                    s.name as source_name,
                    s.version as source_version,
                    1 - (d.embedding <=> %s::vector) as similarity
                FROM documents d
                LEFT JOIN sources s ON d.source_id = s.source_id
                {where_sql}
                ORDER BY d.embedding <=> %s::vector
                LIMIT %s
            """

            cur.execute(query, params)

            results = []
            for row in cur.fetchall():
                results.append(
                    {
                        "document_id": str(row["document_id"]),
                        "title": row["title"],
                        "content": row["content"],
                        "content_type": row["content_type"],
                        "section_path": row["section_path"],
                        "country_context_id": row["country_context_id"],
                        "conditions": row["conditions"],
                        "metadata": row["metadata"],
                        "source_id": str(row["source_id"]) if row["source_id"] else None,
                        "source_name": row["source_name"],
                        "source_version": row["source_version"],
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
                    d.document_id,
                    d.title,
                    d.content,
                    d.content_type,
                    d.section_path,
                    d.country_context_id,
                    d.conditions,
                    d.metadata,
                    d.source_id,
                    d.parent_id,
                    s.name as source_name,
                    s.version as source_version
                FROM documents d
                LEFT JOIN sources s ON d.source_id = s.source_id
                WHERE d.document_id = %s
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
                    "section_path": result["section_path"],
                    "country_context_id": result["country_context_id"],
                    "conditions": result["conditions"],
                    "metadata": result["metadata"],
                    "source_id": str(result["source_id"]) if result["source_id"] else None,
                    "parent_id": str(result["parent_id"]) if result["parent_id"] else None,
                    "source_name": result["source_name"],
                    "source_version": result["source_version"],
                }
            return None
    except Exception:
        return None


def get_documents_by_source(source_id: str) -> List[Dict[str, Any]]:
    """get all documents from a specific source.

    args:
        source_id: source uuid

    returns:
        list of document dicts
    """
    try:
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT 
                    document_id, title, content_type, section_path,
                    country_context_id, conditions, metadata
                FROM documents
                WHERE source_id = %s
                ORDER BY section_path, title
                """,
                (source_id,),
            )
            results = []
            for row in cur.fetchall():
                results.append({
                    "document_id": str(row["document_id"]),
                    "title": row["title"],
                    "content_type": row["content_type"],
                    "section_path": row["section_path"],
                    "country_context_id": row["country_context_id"],
                    "conditions": row["conditions"],
                    "metadata": row["metadata"],
                })
            return results
    except Exception:
        return []


def get_documents_by_condition(
    condition: str,
    country_context_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """get all documents related to a specific medical condition.

    args:
        condition: medical condition to search for
        country_context_id: optional filter by country

    returns:
        list of document dicts
    """
    try:
        with get_db_cursor() as cur:
            if country_context_id:
                cur.execute(
                    """
                    SELECT 
                        document_id, title, content_type, section_path,
                        country_context_id, conditions, metadata
                    FROM documents
                    WHERE %s = ANY(conditions)
                    AND (country_context_id = %s OR country_context_id IS NULL)
                    ORDER BY content_type, title
                    """,
                    (condition, country_context_id),
                )
            else:
                cur.execute(
                    """
                    SELECT 
                        document_id, title, content_type, section_path,
                        country_context_id, conditions, metadata
                    FROM documents
                    WHERE %s = ANY(conditions)
                    ORDER BY content_type, title
                    """,
                    (condition,),
                )
            results = []
            for row in cur.fetchall():
                results.append({
                    "document_id": str(row["document_id"]),
                    "title": row["title"],
                    "content_type": row["content_type"],
                    "section_path": row["section_path"],
                    "country_context_id": row["country_context_id"],
                    "conditions": row["conditions"],
                    "metadata": row["metadata"],
                })
            return results
    except Exception:
        return []
