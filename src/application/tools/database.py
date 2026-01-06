"""database query tool for agent."""

from datetime import datetime
from typing import Optional, Dict, Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from src.infrastructure.persistence.postgres.repositories.users import get_user_by_id
from src.infrastructure.persistence.postgres.repositories.providers import search_providers
from src.infrastructure.persistence.postgres.repositories.appointments import get_user_appointments
from src.infrastructure.persistence.postgres.repositories.interactions import get_user_interactions
from src.infrastructure.persistence.postgres.repositories.consents import get_user_consents
from src.shared.context import current_user_id
from src.shared.logger import get_logger
from src.shared.schemas.tools import DatabaseOutput

logger = get_logger("database")


def serialize_db_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """convert database row to json-serializable dict.

    converts datetime objects to iso format strings so the dict
    can be properly serialized to json by langchain.
    """
    result = {}
    for key, value in row.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            # recursively serialize nested dicts
            result[key] = serialize_db_row(value)
        else:
            result[key] = value
    return result


class DatabaseQueryInput(BaseModel):
    """input schema for database queries."""

    query_type: str = Field(
        description="type of query: 'get_user_by_id', 'get_user_history', 'get_user_interactions', 'get_user_appointments', 'get_providers'"
    )
    limit: Optional[int] = Field(
        10, description="maximum number of results to return (default: 10)"
    )
    specialty: Optional[str] = Field(
        None,
        description="filter providers by specialty (e.g., 'cardiology', 'pediatrics')",
    )


def database_query(
    query_type: str,
    limit: Optional[int] = 10,
    specialty: Optional[str] = None,
) -> Dict[str, Any]:
    """retrieve user data from the database.

    use this tool to:
    - get current user's profile information
    - get current user's interaction history
    - get current user's appointments
    - get available healthcare providers
    - get current user's complete history (profile + interactions + consents)

    note: this tool can only access data for the currently logged-in user. if no user is
    logged in, the tool will return an error. the tool automatically uses the current
    user's id from session context.
    """
    # get current user from context
    user_id = current_user_id.get()

    logger.info(f"database_query called: query_type={query_type}")
    if specialty:
        logger.debug(f"specialty filter: {specialty}")

    try:
        # all queries require user context (security: only access current user's data)
        if not user_id:
            return DatabaseOutput(
                status="error",
                message="no user identified in current session. please ensure you are logged in.",
            ).model_dump()

        # get current user's profile (user_id already set from context)
        if query_type == "get_user_by_id":
            user = get_user_by_id(user_id)
            if user:
                return DatabaseOutput(
                    message="user found", data=serialize_db_row(user)
                ).model_dump()
            else:
                return DatabaseOutput(
                    status="error", message=f"user not found for user_id: {user_id}"
                ).model_dump()

        # get user interactions
        elif query_type == "get_user_interactions":
            interactions = get_user_interactions(user_id, limit=limit)
            if interactions:
                return DatabaseOutput(
                    message=f"found {len(interactions)} interaction(s)",
                    data=[serialize_db_row(i) for i in interactions],
                ).model_dump()
            else:
                return DatabaseOutput(
                    message="no interactions found", data=[]
                ).model_dump()

        # get complete user history (profile + interactions + consents)
        elif query_type == "get_user_history":
            # get user profile
            user = get_user_by_id(user_id)
            if not user:
                return DatabaseOutput(
                    status="error", message=f"user not found for user_id: {user_id}"
                ).model_dump()

            # get interactions
            interactions = get_user_interactions(user_id, limit=limit)

            # get consents
            consents = get_user_consents(user_id, limit=limit)

            result = {
                "user": serialize_db_row(user),
                "interactions": [serialize_db_row(i) for i in interactions],
                "consents": [serialize_db_row(c) for c in consents],
            }
            return DatabaseOutput(
                message="user history retrieved", data=result
            ).model_dump()

        # get user appointments
        elif query_type == "get_user_appointments":
            appointments = get_user_appointments(user_id, limit=limit)
            if appointments:
                return DatabaseOutput(
                    message=f"found {len(appointments)} appointment(s)",
                    data=[serialize_db_row(appt) for appt in appointments],
                ).model_dump()
            else:
                return DatabaseOutput(
                    message="no appointments found", data=[]
                ).model_dump()

        # get available providers (no user context required)
        elif query_type == "get_providers":
            # get current user's country context if available
            country_context = None
            if user_id:
                try:
                    user_data = get_user_by_id(user_id)
                    if user_data:
                        country_context = user_data.get("country_context_id")
                except Exception as e:
                    logger.warning(f"could not get user country context: {e}")
                    # continue without country filter

            providers = search_providers(
                specialty=specialty,
                country_context=country_context,
                limit=limit,
            )

            if providers:
                return DatabaseOutput(
                    message=f"found {len(providers)} provider(s)",
                    data=[serialize_db_row(p) for p in providers],
                ).model_dump()
            else:
                specialty_msg = f" with specialty '{specialty}'" if specialty else ""
                return DatabaseOutput(
                    message=f"no providers found{specialty_msg}", data=[]
                ).model_dump()

        else:
            return DatabaseOutput(
                status="error",
                message=f"unknown query_type '{query_type}'. valid types: get_user_by_id, get_user_interactions, get_user_history, get_user_appointments, get_providers",
            ).model_dump()

    except Exception as e:
        logger.error(f"database query error: {e}", exc_info=True)
        return DatabaseOutput(
            status="error", message=f"database query error: {str(e)}"
        ).model_dump()


database_tool = StructuredTool.from_function(
    func=database_query,
    name="database_query",
    description="""retrieve the current logged-in user's data from the database.

use this tool when:
- you need to access the current user's profile information
- you need to check the current user's past interactions, triage results, or consent records
- you need to view the current user's scheduled appointments
- you need to check available healthcare providers and specialties
- you need to get the current user's complete medical history

important: this tool can only access data for the currently logged-in user.
the tool automatically uses the current session's user - no user identification needed.

query types:
- 'get_user_by_id': retrieve current user's profile information
- 'get_user_interactions': get current user's interaction history (ordered by most recent)
- 'get_user_appointments': get current user's scheduled appointments with provider details
- 'get_providers': get available healthcare providers (optionally filter by specialty)
- 'get_user_history': get current user's complete history including profile, interactions, and consents

examples:
- user asks "what's my phone number?" → use get_user_by_id to get their profile
- user asks "what are my past interactions?" → use get_user_interactions
- user asks "do i have any appointments?" or "show me my appointments" → use get_user_appointments
- user asks "can i see a cardiologist?" or "what specialists are available?" → use get_providers with specialty filter
- user asks "show me my complete history" → use get_user_history

do not use for: creating new records, updating data, deleting records, or accessing other users' data.""",
    args_schema=DatabaseQueryInput,
)
