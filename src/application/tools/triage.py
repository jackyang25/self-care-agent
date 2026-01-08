"""triage and risk flagging tool."""

import logging
from typing import Optional

from src.application.services.triage import (
    assess_fallback_triage,
    assess_verified_triage,
)
from langchain_core.tools import tool
from src.application.tools.schemas.triage import (
    FallbackTriageInput,
    TriageOutput,
    VerifiedTriageInput,
)

logger = logging.getLogger(__name__)


@tool(args_schema=VerifiedTriageInput)
def assess_verified_triage_tool(
    age: Optional[int] = None,
    gender: Optional[str] = None,
    pregnant: Optional[int] = None,
    breathing: Optional[int] = None,
    conscious: Optional[int] = None,
    walking: Optional[int] = None,
    severe_symptom: Optional[int] = None,
    moderate_symptom: Optional[int] = None,
) -> TriageOutput:
    """perform triage using the formally verified verifier.

    use this tool when you have enough verified inputs to run the verifier.

    required verified inputs:
    - age, gender, pregnant, breathing, conscious, walking, severe_symptom, moderate_symptom

    use when: patient describes symptoms requiring urgency assessment; determining if emergency care is needed; triaging clinical concerns.

    do not use for: general health questions without symptoms; appointment scheduling without medical urgency; commodity orders."""

    logger.info(
        f"Received args {{age={age}, gender={gender}, pregnant={pregnant}, breathing={breathing}, conscious={conscious}, walking={walking}, severe_symptom={severe_symptom}, moderate_symptom={moderate_symptom}}}"
    )

    try:
        # enforce completeness so we don't "attempt" verified triage with missing inputs
        missing = []
        for name, val in [
            ("age", age),
            ("gender", gender),
            ("pregnant", pregnant),
            ("breathing", breathing),
            ("conscious", conscious),
            ("walking", walking),
            ("severe_symptom", severe_symptom),
            ("moderate_symptom", moderate_symptom),
        ]:
            if val is None:
                missing.append(name)
        if missing:
            return TriageOutput(
                status="needs_more_info",
                message="verified triage requires these inputs before running. please answer:",
                risk_level="unknown",
                recommendations=missing,
                verification_method="verified",
            )

        triage_result = assess_verified_triage(
            age=age,
            gender=gender,
            pregnant=pregnant,
            breathing=breathing,
            conscious=conscious,
            walking=walking,
            severe_symptom=severe_symptom,
            moderate_symptom=moderate_symptom,
        )

        risk_level = triage_result.risk_level
        verification_method = triage_result.verification_method

    except ValueError as e:
        return TriageOutput(
            status="error",
            message=f"verified triage failed: {str(e)}",
            risk_level="unknown",
            verification_method="verified",
        )

    except Exception as e:
        return TriageOutput(
            status="error",
            message=f"verified triage system error: {str(e)}",
            risk_level="unknown",
            verification_method="verified",
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

    # log structured completion output (similar style to rag tool logs)
    provided_verified_inputs = {
        "age": age is not None,
        "gender": gender is not None,
        "pregnant": pregnant is not None,
        "breathing": breathing is not None,
        "conscious": conscious is not None,
        "walking": walking is not None,
        "severe_symptom": severe_symptom is not None,
        "moderate_symptom": moderate_symptom is not None,
    }
    preview = {
        "risk_level": risk_level,
        "method": verification_method,
        "recommendations": recommendations[:3],
        "provided_verified_inputs": provided_verified_inputs,
    }
    logger.info(f"Completed {{preview={preview}}}")

    return TriageOutput(
        message=f"triage assessment complete: {risk_level} priority ({verification_method} classification)",
        risk_level=risk_level,
        recommendations=recommendations,
        verification_method=verification_method,
    )


@tool(args_schema=FallbackTriageInput)
def assess_fallback_triage_tool(
    symptoms: Optional[str] = None,
    fallback_risk_level: Optional[str] = None,
) -> TriageOutput:
    """perform triage using fallback_risk_level when verified inputs are unavailable."""

    logger.info(
        f"Received args {{symptoms={symptoms[:50] + '...' if symptoms and len(symptoms) > 50 else symptoms}, fallback_risk_level={fallback_risk_level}}}"
    )

    try:
        if fallback_risk_level is None:
            return TriageOutput(
                status="needs_more_info",
                message="fallback triage requires fallback_risk_level ('red', 'yellow', or 'green').",
                risk_level="unknown",
                recommendations=["red", "yellow", "green"],
                symptoms=symptoms,
                verification_method="fallback",
            )

        triage_result = assess_fallback_triage(fallback_risk_level=fallback_risk_level)
        risk_level = triage_result.risk_level
        verification_method = triage_result.verification_method
    except Exception as e:
        return TriageOutput(
            status="error",
            message=f"fallback triage failed: {str(e)}",
            risk_level="unknown",
            symptoms=symptoms,
            verification_method="fallback",
        )

    recommendations = []
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

    preview = {
        "risk_level": risk_level,
        "method": verification_method,
        "recommendations": recommendations[:3],
    }
    logger.info(f"Completed {{preview={preview}}}")

    return TriageOutput(
        message=f"triage assessment complete: {risk_level} priority ({verification_method} classification)",
        risk_level=risk_level,
        recommendations=recommendations,
        verification_method=verification_method,
        symptoms=symptoms,
    )
