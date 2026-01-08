"""triage tool schemas."""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from .base import ToolResponse


class VerifiedTriageInput(BaseModel):
    """input schema for formally verified triage classification."""

    # verified triage inputs (all required for verifier execution)
    age: Optional[int] = Field(
        None, description="verified triage input: patient age in years"
    )
    gender: Optional[str] = Field(
        None,
        description="verified triage input: patient gender (must normalize to 'male' or 'female').",
    )
    pregnant: Optional[int] = Field(
        None,
        description="verified triage input: 1 if pregnant, 0 if not.",
    )
    breathing: Optional[int] = Field(
        None,
        description="verified triage input: 1 if breathing normally, 0 if difficulty/not breathing.",
    )
    conscious: Optional[int] = Field(
        None,
        description="verified triage input: 1 if conscious/alert, 0 if unconscious/altered.",
    )
    walking: Optional[int] = Field(
        None,
        description="verified triage input: 1 if can walk, 0 if cannot.",
    )
    severe_symptom: Optional[int] = Field(
        None,
        description="verified triage input: 1 if severe red-flag symptoms present, 0 if not.",
    )
    moderate_symptom: Optional[int] = Field(
        None,
        description="verified triage input: 1 if moderate concerning symptoms present, 0 if not.",
    )

    @field_validator("gender")
    @classmethod
    def _normalize_gender(cls, value: Optional[str]) -> Optional[str]:
        """Normalize gender to 'male' or 'female' for verified triage."""
        if value is None:
            return None
        s = value.strip().lower()
        if not s:
            return None
        if s in ("male", "m", "man"):
            return "male"
        if s in ("female", "f", "woman"):
            return "female"
        raise ValueError(
            "gender must be 'male' or 'female' (or common variants like 'm'/'f')"
        )


class FallbackTriageInput(BaseModel):
    """input schema for fallback triage classification when verifier inputs are unavailable."""

    symptoms: Optional[str] = Field(
        None,
        description="patient symptoms or complaints. include duration, severity, and key red flags when available.",
    )
    fallback_risk_level: Optional[str] = Field(
        None,
        description="fallback triage category: must be exactly one of 'red', 'yellow', or 'green'.",
    )


class TriageOutput(ToolResponse):
    """output model for triage tool."""

    message: str = Field(..., description="human-readable result message")
    risk_level: Optional[str] = Field(
        None, description="risk level: red, yellow, or green"
    )
    recommendations: Optional[List[str]] = Field(
        None, description="list of clinical recommendations"
    )
    symptoms: Optional[str] = Field(None, description="patient symptoms")
    verification_method: Optional[str] = Field(
        None, description="triage method used: verified or fallback"
    )
