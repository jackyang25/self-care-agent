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


# user service models
class UserProfile(BaseModel):
    """user profile data."""
    
    user_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    country_context_id: Optional[str] = None
    created_at: Optional[str] = None
    
    class Config:
        extra = "allow"


class InteractionRecord(BaseModel):
    """single interaction record."""
    
    interaction_id: str
    user_id: str
    channel: Optional[str] = None
    user_input: Optional[str] = None
    risk_level: Optional[str] = None
    tools_called: Optional[List[str]] = None
    created_at: Optional[str] = None
    
    class Config:
        extra = "allow"


class AppointmentRecord(BaseModel):
    """single appointment record."""
    
    appointment_id: str
    user_id: str
    provider_id: Optional[str] = None
    specialty: Optional[str] = None
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    
    class Config:
        extra = "allow"


class ConsentRecord(BaseModel):
    """single consent record."""
    
    consent_id: str
    user_id: str
    consent_type: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    
    class Config:
        extra = "allow"


class ProviderRecord(BaseModel):
    """healthcare provider record."""
    
    provider_id: str
    name: str
    specialty: Optional[str] = None
    facility: Optional[str] = None
    country_context_id: Optional[str] = None
    
    class Config:
        extra = "allow"


class UserCompleteHistory(BaseModel):
    """complete user history including profile, interactions, and consents."""
    
    user: UserProfile
    interactions: List[InteractionRecord]
    consents: List[ConsentRecord]

