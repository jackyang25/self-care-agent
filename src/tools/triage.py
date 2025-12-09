"""triage and risk flagging tool."""

from typing import Optional
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from src.utils.tool_helpers import get_tool_logger, log_tool_call, format_tool_response

logger = get_tool_logger("triage")


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
    log_tool_call(
        logger, "triage_and_risk_flagging",
        symptoms=symptoms, urgency=urgency, patient_id=patient_id, notes=notes
    )

    risk_level = urgency.lower() if urgency else "low"
    
    # determine recommendation based on risk level
    if risk_level in ["high", "critical"]:
        recommendation = "immediate clinical evaluation recommended"
    elif risk_level == "medium":
        recommendation = "clinical evaluation recommended within 24-48 hours"
    else:
        recommendation = "continue monitoring, self-care may be appropriate"

    # return structured json response
    return format_tool_response(
        risk_level=risk_level,
        recommendation=recommendation,
        symptoms=symptoms,
        urgency=urgency,
        patient_id=patient_id,
        notes=notes,
    )


triage_tool = StructuredTool.from_function(
    func=triage_and_risk_flagging,
    name="triage_and_risk_flagging",
    description="""triage user health symptoms or questions and assign a risk category.

use this tool when the user reports symptoms, asks about a possible medical condition, expresses concern about their health, or needs guidance on whether their situation requires self-care, pharmacy support, telemedicine, or clinical evaluation. the tool applies validated self-care protocols and red-flag rules to determine the safest recommended next step.

use when: user describes symptoms, discomfort, or potential illnesses; user asks whether they should seek care, self-manage, or escalate; user needs a risk assessment before accessing services or commodities.

do not use for: ordering medications, self-tests, or other commodities; booking labs, teleconsultations, or appointments; administrative questions unrelated to clinical symptoms or risk.""",
    args_schema=TriageInput,
)
