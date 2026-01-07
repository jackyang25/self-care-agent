"""provider service output schema."""

from typing import List

from pydantic import BaseModel


class ProviderServiceOutput(BaseModel):
    """output from provider search/lookup service."""
    
    providers: List[dict]  # list for search, single item list for get_by_id
    count: int

