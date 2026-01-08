"""source data access functions for RAG document provenance using ORM."""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from src.infrastructure.postgres.connection import get_db_session
from src.infrastructure.postgres.models import Source

logger = logging.getLogger(__name__)


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
        with get_db_session() as session:
            # check if source exists
            source = session.query(Source).filter(
                Source.source_id == UUID(source_id)
            ).first()
            
            if source:
                # update existing source
                source.name = name
                source.source_type = source_type
                source.country_context_id = country_context_id
                source.version = version
                source.url = url
                source.publisher = publisher
                source.effective_date = effective_date
                source.metadata_ = metadata_json
            else:
                # create new source
                source = Source(
                    source_id=UUID(source_id),
                    name=name,
                    source_type=source_type,
                    country_context_id=country_context_id,
                    version=version,
                    url=url,
                    publisher=publisher,
                    effective_date=effective_date,
                    metadata_=metadata_json,
                )
                session.add(source)
            
            return True
    except Exception:
        logger.exception("insert_source failed")
        return False


def get_source_by_id(source_id: str) -> Optional[Dict[str, Any]]:
    """get source by source_id.

    args:
        source_id: source uuid

    returns:
        source dict or None if not found
    """
    try:
        with get_db_session() as session:
            source = session.query(Source).filter(
                Source.source_id == source_id
            ).first()
            return source.to_dict() if source else None
    except Exception:
        logger.exception("get_source_by_id failed")
        return None


def get_sources_by_country(country_context_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """get all sources, optionally filtered by country.

    args:
        country_context_id: filter by country code, or None for all

    returns:
        list of source dicts
    """
    try:
        with get_db_session() as session:
            query = session.query(Source)
            
            if country_context_id:
                query = query.filter(
                    (Source.country_context_id == country_context_id) |
                    (Source.country_context_id.is_(None))
                )
            
            sources = query.order_by(Source.created_at.desc()).all()
            return [source.to_dict() for source in sources]
    except Exception:
        logger.exception("get_sources_by_country failed")
        return []


def delete_source(source_id: str) -> bool:
    """delete a source by ID (will cascade to documents).

    args:
        source_id: source uuid

    returns:
        True if source was deleted, False otherwise
    """
    try:
        with get_db_session() as session:
            source = session.query(Source).filter(
                Source.source_id == source_id
            ).first()
            
            if source:
                session.delete(source)
                return True
            return False
    except Exception:
        logger.exception("delete_source failed")
        return False
