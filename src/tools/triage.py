"""triage and risk flagging tool."""

from typing import Optional
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from src.utils.tool_helpers import get_tool_logger, log_tool_call, format_tool_response

logger = get_tool_logger("triage")


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


def triage_and_risk_flagging(
    symptoms: Optional[str] = None,
    urgency: Optional[str] = None,
    patient_id: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """assess patient triage and risk level.

    this tool validates and formats triage assessments. you should analyze the symptoms
    first and provide the urgency parameter based on your analysis. consider:
    - symptom severity (mild, moderate, severe)
    - duration and progression
    - red flag symptoms (chest pain, difficulty breathing, etc.)
    - patient safety concerns

    the tool will validate your urgency assessment and provide structured recommendations.
    """
    log_tool_call(
        logger,
        "triage_and_risk_flagging",
        symptoms=symptoms,
        urgency=urgency,
        patient_id=patient_id,
        notes=notes,
    )

    # agent should analyze symptoms and provide urgency parameter
    if urgency:
        risk_level = urgency.strip().lower()
        logger.info(f"using agent-provided urgency: {risk_level}")
    else:
        # fallback: default to yellow (moderate acuity - conservative/safe default)
        # agent should always provide urgency after analyzing symptoms
        logger.warning(
            "no urgency provided by agent, defaulting to 'yellow' (moderate acuity - conservative default)"
        )
        risk_level = "yellow"

    # determine recommendation based on risk level (who iitt)
    if risk_level == "red":
        recommendation = "high acuity - immediate clinical evaluation required"
    elif risk_level == "yellow":
        recommendation = "moderate acuity - clinical evaluation recommended soon"
    else:  # green
        recommendation = "low acuity - can wait, self-care or pharmacy support may be appropriate"

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
    description="""triage user health symptoms and assign a risk category.

**important:** you should analyze the symptoms first, then call this tool with the urgency parameter set based on your analysis. consider:
- symptom severity (mild, moderate, severe, critical)
- duration and progression (acute vs chronic, worsening vs stable)
- red flag symptoms (chest pain, difficulty breathing, severe bleeding, etc.)
- patient safety concerns

**urgency levels (who iitt - interagency integrated triage tool) - you must use exactly these values:**
- 'red': high acuity - immediate attention required (life-threatening conditions, severe symptoms, chest pain, difficulty breathing, severe trauma, stroke, heart attack, signs of deterioration)
- 'yellow': moderate acuity - should be seen soon (moderate-severe symptoms, persistent pain, worsening condition, high fever, concerning symptoms)
- 'green': low acuity - can wait (mild symptoms, stable condition, routine concerns, minor issues that may be managed with self-care or pharmacy support)

**important:** you must use the exact values above. do not use variations like 'critical', 'high', 'medium', 'low', 'urgent', or any other terms. use only: 'red', 'yellow', or 'green'.

**workflow:**
1. analyze the user's symptoms and context
2. determine the appropriate urgency level based on your analysis
3. call this tool with both symptoms and urgency parameters
4. the tool will format your assessment

use this tool when: user describes symptoms, discomfort, or potential illnesses; user asks whether they should seek care, self-manage, or escalate; user needs a risk assessment before accessing services or commodities.

do not use for: ordering medications, self-tests, or other commodities; booking labs, teleconsultations, or appointments; administrative questions unrelated to clinical symptoms or risk.""",
    args_schema=TriageInput,
)
