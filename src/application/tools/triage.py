"""triage and risk flagging tool."""

from typing import Optional, Dict, Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from src.application.services.triage import assess_triage
from src.shared.schemas.tools import TriageOutput


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
    notes: Optional[str] = Field(
        None, description="additional clinical notes or context"
    )
    age: Optional[int] = Field(None, description="patient age")
    gender: Optional[str] = Field(None, description="patient gender")

    # vitals for verified triage (optional)
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


def triage_and_risk_flagging(
    symptoms: Optional[str] = None,
    urgency: Optional[str] = None,
    patient_id: Optional[str] = None,
    notes: Optional[str] = None,
    age: Optional[int] = None,
    gender: Optional[str] = None,
    breathing: Optional[int] = None,
    conscious: Optional[int] = None,
    walking: Optional[int] = None,
    severe_symptom: Optional[int] = None,
    moderate_symptom: Optional[int] = None,
    pregnant: Optional[int] = None,
) -> Dict[str, Any]:
    """assess patient triage and assign risk category.

    args:
        symptoms: patient symptoms or complaints
        urgency: urgency level ('red', 'yellow', or 'green')
        patient_id: patient identifier
        notes: additional clinical notes
        age: patient age (injected from context)
        gender: patient gender (injected from context)
        breathing: 1=normal, 0=difficulty (for verified triage)
        conscious: 1=alert, 0=altered (for verified triage)
        walking: 1=can walk, 0=cannot (for verified triage)
        severe_symptom: 1=severe, 0=not (for verified triage)
        moderate_symptom: 1=moderate, 0=not (for verified triage)
        pregnant: 1=yes, 0=no (for verified triage)

    returns:
        dict with risk level and recommendations
    """

    # assess triage using service layer
    triage_result = assess_triage(
        symptoms=symptoms,
        urgency=urgency,
        age=age,
        gender=gender,
        breathing=breathing,
        conscious=conscious,
        walking=walking,
        severe_symptom=severe_symptom,
        moderate_symptom=moderate_symptom,
    )

    if not triage_result:
        return TriageOutput(
            status="error",
            risk_level="unknown",
            message="triage assessment failed - insufficient information",
        ).model_dump()

    risk_level, score = triage_result

    # map risk level to recommendations
    if risk_level == "emergency":
        recommendations = [
            "seek immediate emergency care",
            "call emergency services or go to nearest emergency department",
            "do not delay - this is a medical emergency",
        ]
    elif risk_level == "urgent":
        recommendations = [
            "seek medical attention within 24 hours",
            "contact your healthcare provider or visit urgent care",
            "monitor symptoms closely",
        ]
    elif risk_level == "routine":
        recommendations = [
            "schedule appointment with healthcare provider",
            "monitor symptoms and seek care if worsens",
            "self-care measures may be appropriate",
        ]
    else:
        recommendations = ["consult healthcare provider for guidance"]

    return TriageOutput(
        risk_level=risk_level,
        triage_score=score,
        recommendations=recommendations,
        message=f"triage assessment complete: {risk_level} priority",
    ).model_dump()


triage_tool = StructuredTool.from_function(
    func=triage_and_risk_flagging,
    name="clinical_triage",
    description="""perform clinical triage and risk assessment.

use this tool when you need to determine medical urgency or risk level based on symptoms. the tool implements who interagency integrated triage tool (iitt) and assigns risk categories.

CRITICAL: you MUST analyze symptoms and provide the 'urgency' parameter as one of: 'red' (emergency), 'yellow' (urgent), or 'green' (routine). base this on:
- red: life-threatening (chest pain, difficulty breathing, severe bleeding, unconsciousness, severe trauma)
- yellow: serious but stable (high fever, moderate pain, concerning symptoms, pregnancy complications)  
- green: non-urgent (mild symptoms, routine concerns, preventive care)

use when: patient describes symptoms requiring urgency assessment; determining if emergency care is needed; triaging clinical concerns.

do not use for: general health questions without symptoms; appointment scheduling without medical urgency; commodity orders.""",
    args_schema=TriageInput,
)
