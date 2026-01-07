"""postgres repositories for data access."""

from src.infrastructure.postgres.repositories.providers import (
    search_providers,
    get_provider_by_id,
    find_provider_for_appointment,
)
from src.infrastructure.postgres.repositories.documents import (
    insert_document,
    search_documents_by_embedding,
    delete_document,
    get_document_by_id,
    get_documents_by_source,
    get_documents_by_condition,
)
from src.infrastructure.postgres.repositories.sources import (
    insert_source,
    get_source_by_id,
    get_sources_by_country,
    delete_source,
)

__all__ = [
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
