"""triage assessment service."""

import os
import subprocess
from typing import Optional, Tuple

import logging

from src.shared.schemas.services import TriageServiceOutput

logger = logging.getLogger(__name__)


def run_verified_triage(
    age: int,
    gender: str,
    pregnant: int,
    breathing: int,
    conscious: int,
    walking: int,
    severe_symptom: int,
    moderate_symptom: int,
) -> Tuple[Optional[str], Optional[int]]:
    """run formally verified triage classification.
    
    calls the verified triage executable which provides provably correct
    classification within the verified logic space.
    
    args:
        age: patient age
        gender: patient gender
        pregnant: 1 if pregnant, 0 if not
        breathing: 1 if breathing normally, 0 if difficulty
        conscious: 1 if conscious and alert, 0 if altered
        walking: 1 if can walk, 0 if cannot
        severe_symptom: 1 if severe symptoms present, 0 if not
        moderate_symptom: 1 if moderate symptoms present, 0 if not
        
    returns:
        tuple of (category, exit_code) where:
        - category: "red", "yellow", or "green" (None if error)
        - exit_code: 0=red, 1=yellow, 2=green (None if error)
    """
    # get path to verified triage executable
    application_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    executable_path = os.path.join(application_dir, "verifiers", "triage-verifier")
    
    if not os.path.exists(executable_path):
        logger.error(f"verified triage executable not found at {executable_path}")
        return None, None
    
    try:
        result = subprocess.run(
            [
                executable_path,
                str(age),
                gender,
                str(pregnant),
                str(breathing),
                str(conscious),
                str(walking),
                str(severe_symptom),
                str(moderate_symptom),
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        
        # map exit codes to categories
        categories = {0: "red", 1: "yellow", 2: "green"}
        category = categories.get(result.returncode)
        
        
        return category, result.returncode
    except subprocess.TimeoutExpired:
        logger.error("verified triage executable timed out")
        return None, None
    except Exception as e:
        logger.error(f"error running verified triage: {e}")
        return None, None


def assess_triage(
    symptoms: Optional[str],
    urgency: Optional[str],
    age: Optional[int] = None,
    gender: Optional[str] = None,
    breathing: Optional[int] = None,
    conscious: Optional[int] = None,
    walking: Optional[int] = None,
    severe_symptom: Optional[int] = None,
    moderate_symptom: Optional[int] = None,
    pregnant: Optional[int] = None,
) -> TriageServiceOutput:
    """assess triage level using verified classification or LLM assessment.
    
    two modes:
    1. verified triage: when all vitals + age/gender provided
    2. llm assessment: when only urgency provided
    
    args:
        symptoms: patient symptoms
        urgency: llm-assessed urgency ('red', 'yellow', 'green')
        age: patient age (for verified triage)
        gender: patient gender (for verified triage)
        breathing: breathing status (for verified triage)
        conscious: consciousness status (for verified triage)
        walking: walking ability (for verified triage)
        severe_symptom: severe symptom indicator (for verified triage)
        moderate_symptom: moderate symptom indicator (for verified triage)
        pregnant: pregnancy status (for verified triage)
        
    returns:
        tuple of (risk_level, verification_method) where:
        - risk_level: "red", "yellow", "green", or "unknown"
        - verification_method: "verified" or "llm"
    """
    risk_level = None
    verification_method = "llm"
    
    # check if we have enough data for verified triage
    vitals_available = all(
        v is not None
        for v in [breathing, conscious, walking, severe_symptom, moderate_symptom]
    )
    
    if vitals_available and age is not None and gender is not None:
        
        # default pregnant to 0 if not provided
        pregnant_value = pregnant if pregnant is not None else 0
        
        # run formally verified triage
        verified_category, exit_code = run_verified_triage(
            age,
            gender,
            pregnant_value,
            breathing,
            conscious,
            walking,
            severe_symptom,
            moderate_symptom,
        )
        
        if verified_category:
            risk_level = verified_category
            verification_method = "verified"
        else:
            logger.warning("verified triage failed, falling back to llm assessment")
    else:
        # log which vitals are missing
        missing = []
        if not vitals_available:
            if breathing is None:
                missing.append("breathing")
            if conscious is None:
                missing.append("conscious")
            if walking is None:
                missing.append("walking")
            if severe_symptom is None:
                missing.append("severe_symptom")
            if moderate_symptom is None:
                missing.append("moderate_symptom")
        if age is None:
            missing.append("age")
        if gender is None:
            missing.append("gender")
        
    
    # fallback to llm-provided urgency if verified triage not used
    if risk_level is None:
        if urgency and urgency.lower() in ["red", "yellow", "green"]:
            risk_level = urgency.lower()
        else:
            risk_level = "unknown"
            logger.warning(f"invalid urgency: {urgency} | result: unknown")
    
    return TriageServiceOutput(
        risk_level=risk_level,
        verification_method=verification_method
    )

