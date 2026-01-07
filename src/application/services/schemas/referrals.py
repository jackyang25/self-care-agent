"""referral service output schema."""

from pydantic import BaseModel


class ReferralServiceOutput(BaseModel):
    """output from provider referral service."""
    
    provider: str
    specialty: str
    facility: str
    date: str
    time: str

