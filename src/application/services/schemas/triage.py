"""triage service output schema."""

from pydantic import BaseModel, Field


class TriageServiceOutput(BaseModel):
    """output from triage assessment service."""
    
    risk_level: str = Field(..., description="risk category: red, yellow, green, or unknown")
    verification_method: str = Field(..., description="triage method: verified or llm")

