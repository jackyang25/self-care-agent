"""provider referral tool."""

from typing import Optional, Dict, Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

import logging

from src.infrastructure.postgres.repositories.providers import find_provider_for_appointment
from src.shared.schemas.tools import ReferralOutput

logger = logging.getLogger(__name__)


class ReferralInput(BaseModel):
    """input schema for provider referrals."""

    specialty: Optional[str] = Field(
        None, description="medical specialty or department"
    )
    provider: Optional[str] = Field(None, description="preferred provider name")
    reason: Optional[str] = Field(
        None, description="reason for referral"
    )


def referrals_and_scheduling(
    specialty: Optional[str] = None,
    provider: Optional[str] = None,
    patient_id: Optional[str] = None,
    preferred_date: Optional[str] = None,
    preferred_time: Optional[str] = None,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """find appropriate healthcare provider for referral.

    args:
        specialty: medical specialty or department
        provider: preferred provider name
        patient_id: patient identifier (unused in config-based system)
        preferred_date: preferred date (for context only)
        preferred_time: preferred time (for context only)
        reason: reason for referral

    returns:
        dict with provider recommendation
    """

    # find appropriate provider
    provider_info = find_provider_for_appointment(
        specialty=specialty,
        provider_name=provider,
    )

    if not provider_info:
        return ReferralOutput(
            status="error",
            message=f"no providers available for specialty: {specialty or 'general_practice'}",
        ).model_dump()

    # return provider recommendation
    return ReferralOutput(
        provider=provider_info.get("name"),
        specialty=provider_info.get("specialty"),
        facility=provider_info.get("facility"),
        date=preferred_date or "contact facility to schedule",
        time=preferred_time or "contact facility for availability",
        status="recommended",
        message=f"recommended provider: {provider_info.get('name')} at {provider_info.get('facility')}",
    ).model_dump()


referral_tool = StructuredTool.from_function(
    func=referrals_and_scheduling,
    name="referrals_and_scheduling",
    description="""recommend healthcare providers for referrals.

use this tool when a user needs to be connected to a healthcare provider or needs information about where to receive care. the tool can find appropriate providers based on specialty and provide facility information.

important: always specify the 'specialty' parameter based on symptoms:
- cardiac/heart symptoms → 'cardiology'
- pregnancy/prenatal → 'obstetrics'
- children (age < 12) → 'pediatrics'
- general health concerns → 'general_practice'

use when: user agrees to or requests a referral to clinical care; user needs information about where to receive care.

do not use for: ordering commodities or medications; pharmacy refills or retail logistics; symptom triage or risk-level determination.""",
    args_schema=ReferralInput,
)
