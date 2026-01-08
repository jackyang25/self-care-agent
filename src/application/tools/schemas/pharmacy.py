"""pharmacy tool schemas."""

from typing import Optional

from pydantic import BaseModel, Field

from .base import ToolResponse


class PharmacyInput(BaseModel):
    """input schema for pharmacy orders."""

    medication: str = Field(
        description="medication name or prescription identifier (required)"
    )
    dosage: Optional[str] = Field(None, description="dosage instructions")
    patient_id: Optional[str] = Field(None, description="patient identifier")
    pharmacy: Optional[str] = Field(None, description="preferred pharmacy location")


class PharmacyOutput(ToolResponse):
    """output model for pharmacy tool."""

    message: str = Field(..., description="human-readable result message")
    prescription_id: Optional[str] = Field(None, description="pharmacy order identifier")
    pharmacy: Optional[str] = Field(None, description="pharmacy name")
    ready_date: Optional[str] = Field(None, description="ready date for pickup")
    medication: Optional[str] = Field(None, description="medication name")
    dosage: Optional[str] = Field(None, description="dosage instructions")
    patient_id: Optional[str] = Field(None, description="patient identifier")

