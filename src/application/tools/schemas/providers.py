"""provider tool schemas."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .base import ToolResponse


class SearchProvidersInput(BaseModel):
    """input for searching providers."""

    specialty: Optional[str] = Field(None, description="provider specialty filter")
    limit: Optional[int] = Field(10, description="maximum number of results")


class GetProviderInput(BaseModel):
    """input for getting a specific provider."""

    provider_id: str = Field(description="provider identifier")


class ProviderOutput(ToolResponse):
    """output model for provider query tools."""

    message: str = Field(..., description="query result message")
    data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(
        None, description="provider data (dict for single provider, list for multiple providers)"
    )

