"""provider search and lookup tools."""

from typing import Optional
from langchain_core.tools import tool

from src.application.services.providers import search_providers, get_provider
from src.application.tools.schemas.providers import SearchProvidersInput, GetProviderInput, ProviderOutput


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
        # call service layer
        result = search_providers(specialty=specialty, limit=limit)
        
        # transform service output to tool output (add presentation layer)
        if result.count > 0:
            return ProviderOutput(
                status="success",
                message=f"found {result.count} provider(s)",
                data=result.providers,
            )
        else:
            return ProviderOutput(
                status="success",
                message="no providers found matching criteria",
                data=[],
            )
    
    except Exception as e:
        return ProviderOutput(
            status="error",
            message=f"provider search failed: {str(e)}",
            data=[],
        )


@tool(args_schema=GetProviderInput)
def get_provider_tool(provider_id: str) -> ProviderOutput:
    """get details for a specific healthcare provider by id.

use this tool when you need detailed information about a specific provider.

use when: user needs specific provider details; user references a provider by id; follow-up on a previous search result.

do not use for: searching for providers (use search_providers_tool); general health questions; appointment booking."""

    try:
        # call service layer
        result = get_provider(provider_id=provider_id)
        
        # transform service output to tool output (add presentation layer)
        return ProviderOutput(
            status="success",
            message="provider found",
            data=result.providers[0],  # single provider
        )
    
    except ValueError as e:
        return ProviderOutput(
            status="error",
            message=str(e),
            data=None,
        )
    
    except Exception as e:
        return ProviderOutput(
            status="error",
            message=f"provider lookup failed: {str(e)}",
            data=None,
        )
