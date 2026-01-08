"""referral tool schemas."""

from typing import Optional

from pydantic import BaseModel, Field

from .base import ToolResponse


class ReferralInput(BaseModel):
    """input schema for provider referrals."""

    specialty: Optional[str] = Field(None, description="medical specialty or department")
    provider: Optional[str] = Field(None, description="preferred provider name")
    patient_id: Optional[str] = Field(None, description="patient identifier")
    preferred_date: Optional[str] = Field(
        None, description="preferred appointment date (free-text if needed)"
    )
    preferred_time: Optional[str] = Field(
        None, description="preferred appointment time (free-text if needed)"
    )
    reason: Optional[str] = Field(None, description="reason for referral")


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

