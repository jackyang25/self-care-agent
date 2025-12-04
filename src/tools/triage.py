"""triage and risk flagging tool."""

from typing import Optional
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


class TriageInput(BaseModel):
    """input schema for triage and risk flagging."""

    symptoms: Optional[str] = Field(None, description="patient symptoms or complaints")
    urgency: Optional[str] = Field(
        None, description="urgency level: low, medium, high, critical"
    )
    patient_id: Optional[str] = Field(None, description="patient identifier")
    notes: Optional[str] = Field(None, description="additional clinical notes")


def triage_and_risk_flagging(
    symptoms: Optional[str] = None,
    urgency: Optional[str] = None,
    patient_id: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """assess patient triage and risk level. use this for evaluating patient symptoms, determining urgency, and flagging high-risk cases."""
    print(f"[TOOL CALLED] triage_and_risk_flagging")
    print(
        f"[ARGUMENTS] symptoms={symptoms}, urgency={urgency}, patient_id={patient_id}, notes={notes}"
    )

    risk_level = urgency.lower() if urgency else "low"
    
    # determine recommendation based on risk level
    if risk_level in ["high", "critical"]:
        recommendation = "immediate clinical evaluation recommended"
    elif risk_level == "medium":
        recommendation = "clinical evaluation recommended within 24-48 hours"
    else:
        recommendation = "continue monitoring, self-care may be appropriate"

    return f"triage assessment completed. risk level: {risk_level}. recommendation: {recommendation}. status: success"


triage_tool = StructuredTool.from_function(
    func=triage_and_risk_flagging,
    name="triage_and_risk_flagging",
    description="""triage user health symptoms or questions and assign a risk category.

use this tool when the user reports symptoms, asks about a possible medical condition, expresses concern about their health, or needs guidance on whether their situation requires self-care, pharmacy support, telemedicine, or clinical evaluation. the tool applies validated self-care protocols and red-flag rules to determine the safest recommended next step.

use when: user describes symptoms, discomfort, or potential illnesses; user asks whether they should seek care, self-manage, or escalate; user needs a risk assessment before accessing services or commodities.

do not use for: ordering medications, self-tests, or other commodities; booking labs, teleconsultations, or appointments; administrative questions unrelated to clinical symptoms or risk.""",
    args_schema=TriageInput,
)
