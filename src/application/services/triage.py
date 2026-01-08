"""triage assessment service."""

import logging
import os
import subprocess
from typing import Optional, Tuple

from src.application.services.schemas.triage import TriageServiceOutput

logger = logging.getLogger(__name__)


def execute_verified_triage(
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
        - category: "red", "yellow", or "green"
        - exit_code: 0=red, 1=yellow, 2=green

    raises:
        FileNotFoundError: if verified triage executable not found
        TimeoutError: if executable times out (>5 seconds)
        RuntimeError: if executable fails to run
    """
    # get path to verified triage executable
    application_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # repo/container ships the verifier as src/application/verifiers/triage
    preferred = os.path.join(application_dir, "verifiers", "triage")
    legacy = os.path.join(application_dir, "verifiers", "triage-verifier")
    executable_path = preferred if os.path.exists(preferred) else legacy

    if not os.path.exists(executable_path):
        raise FileNotFoundError(
            f"verified triage executable not found (checked: {preferred}, {legacy})"
        )

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
        raise TimeoutError("verified triage executable timed out after 5 seconds")
    except Exception as e:
        raise RuntimeError(f"error running verified triage: {e}")


def assess_verified_triage(
    *,
    age: int,
    gender: str,
    pregnant: int,
    breathing: int,
    conscious: int,
    walking: int,
    severe_symptom: int,
    moderate_symptom: int,
) -> TriageServiceOutput:
    """Assess triage using the formally verified verifier."""
    # avoid duplicating full args in logs (tool layer already logs received args)
    logger.info("Attempting verified triage")

    category, exit_code = execute_verified_triage(
        age,
        gender,
        pregnant,
        breathing,
        conscious,
        walking,
        severe_symptom,
        moderate_symptom,
    )
    if not category:
        raise RuntimeError(
            f"verified triage returned unknown category (exit_code={exit_code})"
        )

    logger.info(
        f"Verified triage succeeded {{risk_level={category}, exit_code={exit_code}}}"
    )
    return TriageServiceOutput(risk_level=category, verification_method="verified")


def assess_fallback_triage(*, fallback_risk_level: str) -> TriageServiceOutput:
    """Assess triage using the fallback category when verifier inputs are unavailable."""
    if not fallback_risk_level or fallback_risk_level.lower() not in [
        "red",
        "yellow",
        "green",
    ]:
        raise ValueError(
            "fallback triage requires fallback_risk_level in {'red','yellow','green'}; "
            f"got: {fallback_risk_level}"
        )

    risk_level = fallback_risk_level.lower()
    logger.info(f"Fallback triage used {{risk_level={risk_level}}}")
    return TriageServiceOutput(risk_level=risk_level, verification_method="fallback")
