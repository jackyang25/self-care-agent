"""provider search and lookup service."""

from typing import Optional

from src.infrastructure.postgres.repositories.providers import (
    search_providers as _search_providers,
    get_provider_by_id as _get_provider_by_id,
)
from src.application.services.schemas.providers import ProviderServiceOutput


def search_providers(
    specialty: Optional[str] = None,
    limit: Optional[int] = 10,
) -> ProviderServiceOutput:
    """search for healthcare providers in the database.
    
    finds healthcare providers, optionally filtered by specialty.
    
    args:
        specialty: optional specialty filter
        limit: maximum number of results to return
        
    returns:
        provider search results
        
    raises:
        Exception: if database query fails
    """
    providers = _search_providers(specialty=specialty, limit=limit)
    return ProviderServiceOutput(
        providers=providers or [],
        count=len(providers) if providers else 0,
    )


def get_provider(provider_id: str) -> ProviderServiceOutput:
    """get details for a specific healthcare provider by id.
    
    retrieves detailed information about a specific provider.
    
    args:
        provider_id: unique provider identifier
        
    returns:
        provider details as single-item list
        
    raises:
        ValueError: if provider not found
        Exception: if database query fails
    """
    provider = _get_provider_by_id(provider_id)
    if not provider:
        raise ValueError(f"provider not found: {provider_id}")
    
    return ProviderServiceOutput(
        providers=[provider],
        count=1,
    )

