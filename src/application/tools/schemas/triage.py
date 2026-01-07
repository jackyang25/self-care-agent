"""triage tool schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .base import ToolResponse


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

