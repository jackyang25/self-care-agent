"""pydantic schema for request context.

context passed from frontend with each request, never persisted.
"""

from typing import Optional
from pydantic import BaseModel, Field


class RequestContext(BaseModel):
    """context from frontend for single stateless request.
    
    passed with each request to provide demographic and geographic context.
    used by tools that need age, gender, or country filtering.
    never stored in database - purely ephemeral.
    """
    
    age: Optional[int] = Field(
        None,
        ge=0,
        le=120,
        description="patient age in years"
    )
    gender: Optional[str] = Field(
        None,
        description="patient gender (male, female, other)"
    )
    country: Optional[str] = Field(
        None,
        min_length=2,
        max_length=2,
        description="ISO country code (e.g., za, ke, us)"
    )
    timezone: str = Field(
        default="UTC",
        description="timezone identifier"
    )
