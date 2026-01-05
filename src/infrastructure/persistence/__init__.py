"""persistence layer for database operations."""

# re-export postgres connection utilities for backward compatibility
from src.infrastructure.persistence.postgres.connection import (
    get_db,
    get_db_cursor,
    test_connection,
)

# re-export all repository functions
from src.infrastructure.persistence.postgres.repositories import (
    # users
    get_user_by_email,
    get_user_by_phone,
    get_user_by_id,
    get_user_demographics,
    # interactions
    insert_interaction,
    get_user_interactions,
    # appointments
    create_appointment,
    get_user_appointments,
    get_appointment_by_id,
    update_appointment_status,
    # consents
    get_user_consents,
    # providers
    search_providers,
    get_provider_by_id,
    find_provider_for_appointment,
    # documents
    insert_document,
    search_documents_by_embedding,
    delete_document,
    get_document_by_id,
    get_documents_by_source,
    get_documents_by_condition,
    # sources
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
    "get_user_by_email",
    "get_user_by_phone",
    "get_user_by_id",
    "get_user_demographics",
    # interactions
    "insert_interaction",
    "get_user_interactions",
    # appointments
    "create_appointment",
    "get_user_appointments",
    "get_appointment_by_id",
    "update_appointment_status",
    # consents
    "get_user_consents",
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
