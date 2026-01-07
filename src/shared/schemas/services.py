"""pydantic schemas for service layer outputs.

ensures type safety and validation across service boundaries.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class TriageServiceOutput(BaseModel):
    """output from triage assessment service."""
    
    risk_level: str = Field(..., description="risk category: red, yellow, green, or unknown")
    verification_method: str = Field(..., description="triage method: verified or llm")


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


class CommodityServiceOutput(BaseModel):
    """output from commodity order service."""
    
    order_id: str
    estimated_delivery: str
    items: Optional[str] = None
    quantity: Optional[str] = None
    patient_id: Optional[str] = None
    priority: str


class PharmacyServiceOutput(BaseModel):
    """output from pharmacy order service."""
    
    prescription_id: str
    pharmacy: str
    ready_date: str
    medication: Optional[str] = None
    dosage: Optional[str] = None
    patient_id: Optional[str] = None


class ProviderServiceOutput(BaseModel):
    """output from provider search/lookup service."""
    
    providers: List[dict]  # list for search, single item list for get_by_id
    count: int


class ReferralServiceOutput(BaseModel):
    """output from provider referral service."""
    
    provider: str
    specialty: str
    facility: str
    date: str
    time: str

