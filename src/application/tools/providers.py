"""provider search and lookup tools."""

from typing import Optional
from langchain_core.tools import tool

from src.infrastructure.postgres.repositories.providers import (
    search_providers,
    get_provider_by_id,
)
from src.shared.schemas.tools import SearchProvidersInput, GetProviderInput, ProviderOutput


@tool(args_schema=SearchProvidersInput)
def search_providers_tool(
    specialty: Optional[str] = None,
    limit: Optional[int] = 10,
) -> ProviderOutput:
    """search for healthcare providers in the database.

use this tool when you need to find healthcare providers, optionally filtered by specialty.

use when: user needs to find healthcare providers; user asks about available specialties; user wants to browse provider options.

do not use for: looking up a specific provider by id (use get_provider_tool); general health questions; symptom assessment."""

    try:
        providers = search_providers(specialty=specialty, limit=limit)
        if providers:
            return ProviderOutput(
                message=f"found {len(providers)} provider(s)",
                data=providers,
            )
        else:
            return ProviderOutput(
                message="no providers found matching criteria",
                data=[],
            )

    except Exception as e:
        return ProviderOutput(
            status="error",
            message=f"provider search failed: {str(e)}",
        )


@tool(args_schema=GetProviderInput)
def get_provider_tool(provider_id: str) -> ProviderOutput:
    """get details for a specific healthcare provider by id.

use this tool when you need detailed information about a specific provider.

use when: user needs specific provider details; user references a provider by id; follow-up on a previous search result.

do not use for: searching for providers (use search_providers_tool); general health questions; appointment booking."""

    try:
        provider = get_provider_by_id(provider_id)
        if provider:
            return ProviderOutput(
                message="provider found",
                data=provider,
            )
        else:
            return ProviderOutput(
                status="error",
                message=f"provider not found: {provider_id}",
            )

    except Exception as e:
        return ProviderOutput(
            status="error",
            message=f"provider lookup failed: {str(e)}",
        )
