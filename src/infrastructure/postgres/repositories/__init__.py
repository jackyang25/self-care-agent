"""postgres repositories for data access."""

from src.infrastructure.postgres.repositories.users import (
    get_user_by_email,
    get_user_by_phone,
    get_user_by_id,
    get_user_demographics,
)
from src.infrastructure.postgres.repositories.interactions import (
    insert_interaction,
    get_user_interactions,
)
from src.infrastructure.postgres.repositories.appointments import (
    create_appointment,
    get_user_appointments,
    get_appointment_by_id,
    update_appointment_status,
)
from src.infrastructure.postgres.repositories.consents import get_user_consents
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

