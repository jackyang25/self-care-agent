"""pydantic schemas for service layer outputs.

ensures type safety and validation across service boundaries.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class TriageServiceOutput(BaseModel):
    """output from triage assessment service."""
    
    risk_level: str = Field(..., description="risk category: red, yellow, green, or unknown")
    verification_method: str = Field(..., description="triage method: verified or llm")


class AppointmentServiceOutput(BaseModel):
    """output from appointment scheduling service."""
    
    appointment_id: str
    provider: str
    specialty: str
    facility: str
    date: str
    time: str
    status: str
    confirmation_code: Optional[str] = None


class DocumentSearchResult(BaseModel):
    """single document from RAG search."""
    
    title: str
    content: str
    similarity: float
    source_name: Optional[str] = None
    source_version: Optional[str] = None
    content_type: Optional[str] = None
    country_context_id: Optional[str] = None
    conditions: Optional[List[str]] = None


class InteractionServiceOutput(BaseModel):
    """output from interaction save service."""
    
    interaction_id: str
    success: bool


class SourceServiceOutput(BaseModel):
    """output from source storage service."""
    
    source_id: str
    success: bool


class DocumentServiceOutput(BaseModel):
    """output from document storage service."""
    
    document_id: str
    success: bool

