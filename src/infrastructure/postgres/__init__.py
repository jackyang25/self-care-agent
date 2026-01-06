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
    cancel_appointment,
    get_user_consents,
    search_providers,
    find_provider_for_appointment,
    get_documents_by_content_type,
    get_documents_by_ids,
    search_documents_by_embedding,
    get_source_by_title,
    get_sources_by_content_type,
    insert_source,
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
    "cancel_appointment",
    # consents
    "get_user_consents",
    # providers
    "search_providers",
    "find_provider_for_appointment",
    # documents
    "get_documents_by_content_type",
    "get_documents_by_ids",
    "search_documents_by_embedding",
    # sources
    "get_source_by_title",
    "get_sources_by_content_type",
    "insert_source",
]
