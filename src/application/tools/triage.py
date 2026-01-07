"""triage and risk flagging tool."""

from typing import Optional

from langchain_core.tools import tool

from src.application.services.triage import assess_triage
from src.application.tools.schemas.triage import TriageInput, TriageOutput


@tool(args_schema=TriageInput)
def triage_tool(
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
) -> TriageOutput:
    """perform clinical triage and risk assessment.

use this tool when you need to determine medical urgency or risk level based on symptoms. the tool implements who interagency integrated triage tool (iitt) and assigns risk categories.

CRITICAL: you MUST analyze symptoms and provide the 'urgency' parameter as one of: 'red' (emergency), 'yellow' (urgent), or 'green' (routine). base this on:
- red: life-threatening (chest pain, difficulty breathing, severe bleeding, unconsciousness, severe trauma)
- yellow: serious but stable (high fever, moderate pain, concerning symptoms, pregnancy complications)  
- green: non-urgent (mild symptoms, routine concerns, preventive care)

use when: patient describes symptoms requiring urgency assessment; determining if emergency care is needed; triaging clinical concerns.

do not use for: general health questions without symptoms; appointment scheduling without medical urgency; commodity orders."""

    try:
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
            pregnant=pregnant,
        )

        risk_level = triage_result.risk_level
        verification_method = triage_result.verification_method

    except ValueError as e:
        return TriageOutput(
            status="error",
            message=f"triage failed: {str(e)}",
            risk_level="unknown",
            symptoms=symptoms,
            patient_id=patient_id,
            notes=notes,
        )
    
    except Exception as e:
        return TriageOutput(
            status="error",
            message=f"triage system error: {str(e)}",
            risk_level="unknown",
            symptoms=symptoms,
            patient_id=patient_id,
            notes=notes,
        )

    # map risk level to recommendations (red = emergency, yellow = urgent, green = routine)
    if risk_level == "red":
        recommendations = [
            "seek immediate emergency care",
            "call emergency services or go to nearest emergency department",
            "do not delay - this is a medical emergency",
        ]
    elif risk_level == "yellow":
        recommendations = [
            "seek medical attention within 24 hours",
            "contact your healthcare provider or visit urgent care",
            "monitor symptoms closely",
        ]
    elif risk_level == "green":
        recommendations = [
            "schedule appointment with healthcare provider",
            "monitor symptoms and seek care if worsens",
            "self-care measures may be appropriate",
        ]
    else:
        recommendations = ["consult healthcare provider for guidance"]

    return TriageOutput(
        message=f"triage assessment complete: {risk_level} priority ({verification_method} classification)",
        risk_level=risk_level,
        recommendations=recommendations,
        verification_method=verification_method,
        symptoms=symptoms,
        patient_id=patient_id,
        notes=notes,
    )
