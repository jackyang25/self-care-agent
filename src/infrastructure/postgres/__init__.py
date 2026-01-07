"""postgres persistence layer - connection and repositories."""

from src.infrastructure.postgres.connection import (
    get_db_session,
    test_connection,
)
from src.infrastructure.postgres.repositories import (
    search_providers,
    get_provider_by_id,
    find_provider_for_appointment,
    insert_document,
    search_documents_by_embedding,
    delete_document,
    get_document_by_id,
    get_documents_by_source,
    get_documents_by_condition,
    insert_source,
    get_source_by_id,
    get_sources_by_country,
    delete_source,
)

__all__ = [
    # connection
    "get_db_session",
    "test_connection",
    # providers
    "search_providers",
    "get_provider_by_id",
    "find_provider_for_appointment",
    # documents
    "insert_document",
    "search_documents_by_embedding",
    "delete_document",
    "get_document_by_id",
    "get_documents_by_source",
    "get_documents_by_condition",
    # sources
    "insert_source",
    "get_source_by_id",
    "get_sources_by_country",
    "delete_source",
]
