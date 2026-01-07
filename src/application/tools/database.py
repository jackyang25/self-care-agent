"""database query tool for providers."""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from src.infrastructure.postgres.repositories.providers import (
    search_providers,
    get_provider_by_id,
)


class DatabaseQueryInput(BaseModel):
    """input for database query tool."""

    query_type: str = Field(
        description="Type of query: 'search_providers' or 'get_provider'"
    )
    limit: Optional[int] = Field(default=10, description="Max results")
    specialty: Optional[str] = Field(default=None, description="Provider specialty filter")
    provider_id: Optional[str] = Field(default=None, description="Provider ID for specific lookup")


class DatabaseOutput(BaseModel):
    """output from database query."""

    status: str = Field(default="success", description="Status of query")
    message: str = Field(description="Human-readable result message")
    data: Optional[Any] = Field(default=None, description="Query results")


def database_query(
    query_type: str,
    limit: Optional[int] = 10,
    specialty: Optional[str] = None,
    provider_id: Optional[str] = None,
) -> Dict[str, Any]:
    """query healthcare providers from database.

    args:
        query_type: type of query ('search_providers' or 'get_provider')
        limit: max results to return (default: 10)
        specialty: filter providers by specialty
        provider_id: specific provider ID to look up

    returns:
        dict with query results
    """

    try:
        if query_type == "search_providers":
            providers = search_providers(specialty=specialty, limit=limit)
            if providers:
                return DatabaseOutput(
                    message=f"found {len(providers)} provider(s)",
                    data=providers,
                ).model_dump()
            else:
                return DatabaseOutput(
                    message="no providers found matching criteria",
                    data=[],
                ).model_dump()

        elif query_type == "get_provider":
            if not provider_id:
                return DatabaseOutput(
                    status="error",
                    message="provider_id required for get_provider query",
                ).model_dump()

            provider = get_provider_by_id(provider_id)
            if provider:
                return DatabaseOutput(
                    message="provider found",
                    data=provider,
                ).model_dump()
            else:
                return DatabaseOutput(
                    status="error",
                    message=f"provider not found: {provider_id}",
                ).model_dump()

        else:
            return DatabaseOutput(
                status="error",
                message=f"unsupported query_type: {query_type}. use 'search_providers' or 'get_provider'",
            ).model_dump()

    except Exception as e:
        return DatabaseOutput(
            status="error", message=f"database query failed: {str(e)}"
        ).model_dump()
