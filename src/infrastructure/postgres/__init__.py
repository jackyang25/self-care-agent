"""postgres persistence layer - connection and repositories."""

from src.infrastructure.postgres.connection import (
    get_db,
    get_db_cursor,
    test_connection,
)
from src.infrastructure.postgres.repositories import (
    get_user_by_id,
    get_user_by_phone,
    get_user_by_email,
    get_user_demographics,
    insert_interaction,
    get_user_interactions,
    get_user_appointments,
    create_appointment,
    update_appointment_status,
    get_user_consents,
    search_providers,
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
    "get_db",
    "get_db_cursor",
    "test_connection",
    # users
    "get_user_by_id",
    "get_user_by_phone",
    "get_user_by_email",
    "get_user_demographics",
    # interactions
    "insert_interaction",
    "get_user_interactions",
    # appointments
    "get_user_appointments",
    "create_appointment",
    "update_appointment_status",
    # consents
    "get_user_consents",
    # providers
    "search_providers",
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
