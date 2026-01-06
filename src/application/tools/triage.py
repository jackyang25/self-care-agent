"""triage and risk flagging tool."""

from typing import Optional, Dict, Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from src.application.services.triage import assess_triage
from src.application.services.users import get_user_demographics
from src.shared.logger import get_tool_logger, log_tool_call
from src.shared.schemas.tools import TriageOutput

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
        breathing: 1=normal, 0=difficulty (for verified triage)
        conscious: 1=alert, 0=altered (for verified triage)
        walking: 1=can walk, 0=cannot (for verified triage)
        severe_symptom: 1=severe, 0=not (for verified triage)
        moderate_symptom: 1=moderate, 0=not (for verified triage)
        pregnant: 1=yes, 0=no (for verified triage)

    returns:
        dict with risk level and recommendations
    """
    log_tool_call(
        logger,
        "triage_and_risk_flagging",
        symptoms=symptoms,
        urgency=urgency,
        patient_id=patient_id,
        notes=notes,
        breathing=breathing,
        conscious=conscious,
        walking=walking,
        severe_symptom=severe_symptom,
        moderate_symptom=moderate_symptom,
        pregnant=pregnant,
    )

    # get user demographics for verified triage (if needed)
    age, gender = get_user_demographics()

    # assess triage using service layer
    risk_level, verification_method = assess_triage(
        symptoms=symptoms,
        urgency=urgency,
        age=age,
        gender=gender,
        breathing=breathing,
        conscious=conscious,
        walking=walking,
        severe_symptom=severe_symptom,
        moderate_symptom=moderate_symptom,
        pregnant=pregnant,
    )

    # determine recommendation based on risk level (who iitt)
    if risk_level == "red":
        recommendation = "high acuity - immediate clinical evaluation required"
    elif risk_level == "yellow":
        recommendation = "moderate acuity - clinical evaluation recommended soon"
    elif risk_level == "green":
        recommendation = (
            "low acuity - can wait, self-care or pharmacy support may be appropriate"
        )
    else:  # unknown
        recommendation = (
            "unable to assess risk - insufficient information. gather either: "
            "(1) urgency assessment based on symptom analysis, or "
            "(2) complete vitals for verified triage"
        )

    # check if vitals were provided (for output model)
    vitals_available = all(
        v is not None
        for v in [breathing, conscious, walking, severe_symptom, moderate_symptom]
    )

    # return pydantic model instance
    vitals_dict = (
        {
            "breathing": breathing,
            "conscious": conscious,
            "walking": walking,
            "severe_symptom": severe_symptom,
            "moderate_symptom": moderate_symptom,
            "pregnant": pregnant,
        }
        if vitals_available
        else None
    )

    # return pydantic model instance
    return TriageOutput(
        risk_level=risk_level,
        recommendation=recommendation,
        symptoms=symptoms,
        urgency=urgency,
        patient_id=patient_id,
        notes=notes,
        verification_method=verification_method,
        vitals=vitals_dict,
    ).model_dump()


triage_tool = StructuredTool.from_function(
    func=triage_and_risk_flagging,
    name="triage_and_risk_flagging",
    description="""triage user health symptoms and assign a risk category.

**two triage modes:**

1. **verified triage (use for serious/uncertain cases)**: when you gather structured vitals, the tool uses a formally verified classification system for enhanced safety and logical correctness.
   - gather from conversation: breathing (1=normal, 0=difficulty), conscious (1=alert, 0=altered), walking (1=can walk, 0=cannot)
   - assess from symptoms: severe_symptom (1=severe, 0=not), moderate_symptom (1=moderate, 0=not)
   - ask if relevant: pregnant (1=yes, 0=no) - only for female patients when clinically relevant
   - the tool automatically fetches age/gender from user's profile
   - provides provably correct classification within verified logic space

2. **llm-based triage (use for clearly minor cases)**: when vitals not gathered, provide your urgency assessment and the tool will format your assessment.

**urgency levels (who iitt - interagency integrated triage tool) - you must use exactly these values:**
- 'red': high acuity - immediate attention required (life-threatening conditions, severe symptoms, chest pain, difficulty breathing, severe trauma, stroke, heart attack, signs of deterioration)
- 'yellow': moderate acuity - should be seen soon (moderate-severe symptoms, persistent pain, worsening condition, high fever, concerning symptoms)
- 'green': low acuity - can wait (mild symptoms, stable condition, routine concerns, minor issues that may be managed with self-care or pharmacy support)

**important:** you must use the exact values above. do not use variations like 'critical', 'high', 'medium', 'low', 'urgent', or any other terms. use only: 'red', 'yellow', or 'green'.

**when to gather vitals for verified triage (recommended for safety-critical cases):**
- severe symptoms: chest pain, difficulty breathing, severe bleeding, unconscious, stroke symptoms, severe trauma
- moderate symptoms with uncertainty: unclear severity, multiple symptoms, progressive worsening
- high-risk patients: if you suspect patient may be pregnant, elderly (>65), or infant
- user explicitly asks: "should I go to ER?", "is this an emergency?"
- borderline cases: when you're unsure between RED and YELLOW

**when llm assessment is sufficient (for clearly minor cases):**
- obviously minor: small cuts, mild headache, minor bruise, vitamin questions
- routine health questions: general wellness, prevention, educational queries
- follow-up after triage: already triaged in current conversation

**workflow:**
1. analyze the user's symptoms and assess severity
2. **if serious/uncertain** → ask questions to gather vitals for verified triage:
   - breathing: "are you having any difficulty breathing?" (1=normal, 0=difficulty)
   - conscious: assess from conversation or ask "are you feeling alert and clear-headed?" (1=alert, 0=altered)
   - walking: "are you able to walk right now?" (1=yes, 0=no)
   - severe symptoms: assess if severe/critical (severe pain, severe bleeding, etc.) (1=yes, 0=no)
   - moderate symptoms: assess if moderate but not severe (1=yes, 0=no)
   - pregnant (if female): "are you pregnant?" when relevant (1=yes, 0=no)
3. **if clearly minor** → assess urgency and call tool with your assessment (no vitals needed)
4. call this tool with gathered information and provide recommendations to user

**example gathering flow:**
user: "i have a headache"
you: "i'm sorry to hear that. to assess this properly, i need to ask a few quick questions. are you having any difficulty breathing?"
user: "no, i'm breathing fine"
you: "good. are you able to walk around?"
user: "yes"
you: "would you describe the headache as severe or moderate?"
user: "it's pretty bad"
you: *calls tool with all vitals: breathing=1, conscious=1, walking=1, severe=1, moderate=0*

use this tool when: user describes symptoms, discomfort, or potential illnesses; user asks whether they should seek care, self-manage, or escalate; user needs a risk assessment before accessing services or commodities.

do not use for: ordering medications, self-tests, or other commodities; booking labs, teleconsultations, or appointments; administrative questions unrelated to clinical symptoms or risk.""",
    args_schema=TriageInput,
)
