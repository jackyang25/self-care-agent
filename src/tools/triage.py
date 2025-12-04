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

    return f"triage assessment completed. risk level: {risk_level}. recommendation: continue monitoring. status: success"


triage_tool = StructuredTool.from_function(
    func=triage_and_risk_flagging,
    name="triage_and_risk_flagging",
    description="assess patient triage and risk level. use for evaluating symptoms, determining urgency, and flagging high-risk cases.",
    args_schema=TriageInput,
)
