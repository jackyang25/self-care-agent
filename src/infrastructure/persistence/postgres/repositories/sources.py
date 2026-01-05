"""source data access functions for RAG document provenance."""

from typing import List, Optional, Dict, Any
from src.infrastructure.persistence.postgres.connection import get_db_cursor


def insert_source(
    source_id: str,
    name: str,
    source_type: str,
    country_context_id: Optional[str] = None,
    version: Optional[str] = None,
    url: Optional[str] = None,
    publisher: Optional[str] = None,
    effective_date: Optional[str] = None,
    metadata_json: Optional[str] = None,
) -> bool:
    """insert a source record into database.

    args:
        source_id: unique source id
        name: source name (e.g., "APC 2023 Clinical Tool")
        source_type: type classification (e.g., "clinical_guideline", "protocol")
        country_context_id: country code (e.g., "za", "ke") or None for global
        version: version string
        url: original source URL
        publisher: publishing organization
        effective_date: date source became effective (YYYY-MM-DD)
        metadata_json: additional metadata as json string

    returns:
        True if successful, False otherwise
    """
    try:
        with get_db_cursor() as cur:
            cur.execute(
                """
                INSERT INTO sources (
                    source_id, name, source_type, country_context_id,
                    version, url, publisher, effective_date, metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (source_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    source_type = EXCLUDED.source_type,
                    country_context_id = EXCLUDED.country_context_id,
                    version = EXCLUDED.version,
                    url = EXCLUDED.url,
                    publisher = EXCLUDED.publisher,
                    effective_date = EXCLUDED.effective_date,
                    metadata = EXCLUDED.metadata
                """,
                (
                    source_id,
                    name,
                    source_type,
                    country_context_id,
                    version,
                    url,
                    publisher,
                    effective_date,
                    metadata_json,
                ),
            )
            return True
    except Exception:
        return False


def get_source_by_id(source_id: str) -> Optional[Dict[str, Any]]:
    """get source by source_id.

    args:
        source_id: source uuid

    returns:
        source dict or None if not found
    """
    try:
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT 
                    source_id,
                    name,
                    source_type,
                    country_context_id,
                    version,
                    url,
                    publisher,
                    effective_date,
                    metadata,
                    created_at
                FROM sources
                WHERE source_id = %s
                """,
                (source_id,),
            )
            result = cur.fetchone()
            if result:
                return {
                    "source_id": str(result["source_id"]),
                    "name": result["name"],
                    "source_type": result["source_type"],
                    "country_context_id": result["country_context_id"],
                    "version": result["version"],
                    "url": result["url"],
                    "publisher": result["publisher"],
                    "effective_date": str(result["effective_date"]) if result["effective_date"] else None,
                    "metadata": result["metadata"],
                    "created_at": str(result["created_at"]),
                }
            return None
    except Exception:
        return None


def get_sources_by_country(country_context_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """get all sources, optionally filtered by country.

    args:
        country_context_id: filter by country code, or None for all

    returns:
        list of source dicts
    """
    try:
        with get_db_cursor() as cur:
            if country_context_id:
                cur.execute(
                    """
                    SELECT 
                        source_id, name, source_type, country_context_id,
                        version, url, publisher, effective_date, metadata, created_at
                    FROM sources
                    WHERE country_context_id = %s OR country_context_id IS NULL
                    ORDER BY created_at DESC
                    """,
                    (country_context_id,),
                )
            else:
                cur.execute(
                    """
                    SELECT 
                        source_id, name, source_type, country_context_id,
                        version, url, publisher, effective_date, metadata, created_at
                    FROM sources
                    ORDER BY created_at DESC
                    """
                )
            
            results = []
            for row in cur.fetchall():
                results.append({
                    "source_id": str(row["source_id"]),
                    "name": row["name"],
                    "source_type": row["source_type"],
                    "country_context_id": row["country_context_id"],
                    "version": row["version"],
                    "url": row["url"],
                    "publisher": row["publisher"],
                    "effective_date": str(row["effective_date"]) if row["effective_date"] else None,
                    "metadata": row["metadata"],
                    "created_at": str(row["created_at"]),
                })
            return results
    except Exception:
        return []


def delete_source(source_id: str) -> bool:
    """delete a source by ID (will cascade to documents).

    args:
        source_id: source uuid

    returns:
        True if source was deleted, False otherwise
    """
    try:
        with get_db_cursor() as cur:
            cur.execute("DELETE FROM sources WHERE source_id = %s", (source_id,))
            return cur.rowcount > 0
    except Exception:
        return False

