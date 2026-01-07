"""pydantic schemas for tool inputs and outputs."""

from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field


# base models

class ToolResponse(BaseModel):
    """base tool response model."""

    status: str = Field(default="success", description="response status")


# input schemas

class TriageInput(BaseModel):
    """input schema for triage and risk flagging."""

    symptoms: Optional[str] = Field(
        None,
        description="patient symptoms or complaints. analyze the symptoms to determine urgency level.",
    )
    urgency: Optional[str] = Field(
        None,
        description="urgency level using who iitt (interagency integrated triage tool). must be exactly one of: 'red', 'yellow', or 'green'. analyze the symptoms first and provide this parameter based on your analysis. consider: severity, duration, red flags, and patient safety.",
    )
    patient_id: Optional[str] = Field(None, description="patient identifier")
    notes: Optional[str] = Field(None, description="additional clinical notes or context")
    age: Optional[int] = Field(None, description="patient age")
    gender: Optional[str] = Field(None, description="patient gender")
    breathing: Optional[int] = Field(
        None,
        description="1 if patient is breathing normally, 0 if not breathing or difficulty breathing. gather from conversation.",
    )
    conscious: Optional[int] = Field(
        None,
        description="1 if patient is conscious and alert, 0 if unconscious or altered mental status. gather from conversation.",
    )
    walking: Optional[int] = Field(
        None,
        description="1 if patient can walk, 0 if cannot walk or mobility impaired. gather from conversation.",
    )
    severe_symptom: Optional[int] = Field(
        None,
        description="1 if severe symptoms present (severe pain, severe bleeding, critical condition), 0 if not. assess from symptoms.",
    )
    moderate_symptom: Optional[int] = Field(
        None,
        description="1 if moderate symptoms present (moderate pain, fever, concerning symptoms), 0 if not. assess from symptoms.",
    )
    pregnant: Optional[int] = Field(
        None,
        description="1 if patient is pregnant, 0 if not. ask if patient is female and symptoms warrant.",
    )


class CommodityInput(BaseModel):
    """input schema for commodity orders."""

    items: Optional[str] = Field(None, description="list of items to order")
    quantity: Optional[str] = Field(None, description="quantities for each item")
    patient_id: Optional[str] = Field(None, description="patient identifier")
    priority: Optional[str] = Field(None, description="order priority: normal, urgent")


class PharmacyInput(BaseModel):
    """input schema for pharmacy orders."""

    medication: Optional[str] = Field(None, description="medication name or prescription")
    dosage: Optional[str] = Field(None, description="dosage instructions")
    patient_id: Optional[str] = Field(None, description="patient identifier")
    pharmacy: Optional[str] = Field(None, description="preferred pharmacy location")


class ReferralInput(BaseModel):
    """input schema for provider referrals."""

    specialty: Optional[str] = Field(None, description="medical specialty or department")
    provider: Optional[str] = Field(None, description="preferred provider name")
    reason: Optional[str] = Field(None, description="reason for referral")


class RAGInput(BaseModel):
    """input schema for RAG retrieval."""

    query: str = Field(
        description="search query for finding relevant clinical information, guidelines, or protocols"
    )
    content_type: Optional[str] = Field(
        None,
        description="filter by content type (e.g., 'guideline', 'protocol', 'medication_info')",
    )
    content_types: Optional[List[str]] = Field(
        None,
        description="filter by multiple content types (e.g., ['guideline', 'protocol'])",
    )
    conditions: Optional[List[str]] = Field(
        None,
        description="filter by medical conditions (e.g., ['fever', 'malaria', 'tb'])",
    )
    country: Optional[str] = Field(
        None,
        description="country context for region-specific guidelines (e.g., 'za', 'ke')",
    )
    limit: Optional[int] = Field(
        5, description="maximum number of documents to retrieve (default: 5)"
    )


class SearchProvidersInput(BaseModel):
    """input for searching providers."""

    specialty: Optional[str] = Field(None, description="provider specialty filter")
    limit: Optional[int] = Field(10, description="maximum number of results")


class GetProviderInput(BaseModel):
    """input for getting a specific provider."""

    provider_id: str = Field(description="provider identifier")


# output schemas


class TriageOutput(ToolResponse):
    """output model for triage tool."""

    message: str = Field(..., description="human-readable result message")
    risk_level: Optional[str] = Field(None, description="risk level: red, yellow, or green")
    recommendations: Optional[List[str]] = Field(None, description="list of clinical recommendations")
    triage_score: Optional[float] = Field(None, description="numeric triage score")
    symptoms: Optional[str] = Field(None, description="patient symptoms")
    patient_id: Optional[str] = Field(None, description="patient identifier")
    notes: Optional[str] = Field(None, description="additional notes")
    verification_method: Optional[str] = Field(None, description="triage method used: verified or llm")
    vitals: Optional[Dict[str, Any]] = Field(None, description="vital signs")


class PharmacyOutput(ToolResponse):
    """output model for pharmacy tool."""

    message: str = Field(..., description="human-readable result message")
    prescription_id: Optional[str] = Field(None, description="pharmacy order identifier")
    pharmacy: Optional[str] = Field(None, description="pharmacy name")
    ready_date: Optional[str] = Field(None, description="ready date for pickup")
    medication: Optional[str] = Field(None, description="medication name")
    dosage: Optional[str] = Field(None, description="dosage instructions")
    patient_id: Optional[str] = Field(None, description="patient identifier")


class CommodityOutput(ToolResponse):
    """output model for commodity tool."""

    message: str = Field(..., description="human-readable result message")
    order_id: Optional[str] = Field(None, description="commodity order identifier")
    estimated_delivery: Optional[str] = Field(None, description="estimated delivery date")
    items: Optional[str] = Field(None, description="ordered items")
    quantity: Optional[str] = Field(None, description="item quantities")
    patient_id: Optional[str] = Field(None, description="patient identifier")
    priority: Optional[str] = Field(None, description="order priority")


class ReferralOutput(ToolResponse):
    """output model for referral tool."""

    message: str = Field(..., description="human-readable result message")
    appointment_id: Optional[str] = Field(None, description="appointment identifier")
    provider: Optional[str] = Field(None, description="provider name")
    specialty: Optional[str] = Field(None, description="provider specialty")
    facility: Optional[str] = Field(None, description="facility name")
    date: Optional[str] = Field(None, description="appointment date")
    time: Optional[str] = Field(None, description="appointment time")
    reason: Optional[str] = Field(None, description="reason for appointment")


class RAGOutput(ToolResponse):
    """output model for rag retrieval tool."""

    message: str = Field(..., description="human-readable result message")
    documents: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="retrieved documents")
    query: Optional[str] = Field(None, description="search query")
    count: Optional[int] = Field(None, description="number of results found")


class ProviderOutput(ToolResponse):
    """output model for provider query tools."""

    message: str = Field(..., description="query result message")
    data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(
        None, description="provider data (dict for single provider, list for multiple providers)"
    )
