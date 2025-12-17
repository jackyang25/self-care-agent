"""pydantic output models for tool responses."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ToolResponse(BaseModel):
    """base tool response model."""

    status: str = Field(default="success", description="response status")


class TriageOutput(ToolResponse):
    """output model for triage tool."""

    risk_level: str = Field(..., description="risk level: red, yellow, or green")
    recommendation: str = Field(..., description="clinical recommendation")
    symptoms: Optional[str] = Field(None, description="patient symptoms")
    urgency: Optional[str] = Field(None, description="urgency level")
    patient_id: Optional[str] = Field(None, description="patient identifier")
    notes: Optional[str] = Field(None, description="additional notes")
    verification_method: Optional[str] = Field(None, description="triage method used")
    vitals: Optional[Dict[str, Any]] = Field(None, description="vital signs")


class PharmacyOutput(ToolResponse):
    """output model for pharmacy tool."""

    prescription_id: str = Field(..., description="pharmacy order identifier")
    pharmacy: Optional[str] = Field(None, description="pharmacy name")
    ready_date: Optional[str] = Field(None, description="ready date for pickup")
    medication: Optional[str] = Field(None, description="medication name")
    dosage: Optional[str] = Field(None, description="dosage instructions")
    patient_id: Optional[str] = Field(None, description="patient identifier")


class CommodityOutput(ToolResponse):
    """output model for commodity tool."""

    order_id: str = Field(..., description="commodity order identifier")
    estimated_delivery: Optional[str] = Field(
        None, description="estimated delivery date"
    )
    items: Optional[str] = Field(None, description="ordered items")
    quantity: Optional[str] = Field(None, description="item quantities")
    patient_id: Optional[str] = Field(None, description="patient identifier")
    priority: Optional[str] = Field(None, description="order priority")


class ReferralOutput(ToolResponse):
    """output model for referral tool."""

    appointment_id: Optional[str] = Field(None, description="appointment identifier")
    provider: Optional[str] = Field(None, description="provider name")
    specialty: Optional[str] = Field(None, description="provider specialty")
    facility: Optional[str] = Field(None, description="facility name")
    date: Optional[str] = Field(None, description="appointment date")
    time: Optional[str] = Field(None, description="appointment time")
    reason: Optional[str] = Field(None, description="reason for appointment")


class RAGOutput(ToolResponse):
    """output model for rag retrieval tool."""

    query: str = Field(..., description="search query")
    results_count: int = Field(..., description="number of results found")
    documents: List[Dict[str, Any]] = Field(..., description="retrieved documents")


class DatabaseOutput(ToolResponse):
    """output model for database query tool."""

    message: str = Field(..., description="query result message")
    data: Optional[Dict[str, Any]] = Field(None, description="retrieved data")
