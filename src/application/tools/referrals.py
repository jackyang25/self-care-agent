"""provider referral tool."""

from typing import Optional

from langchain_core.tools import tool

from src.infrastructure.postgres.repositories.providers import find_provider_for_appointment
from src.shared.schemas.tools import ReferralInput, ReferralOutput


@tool(args_schema=ReferralInput)
def referral_tool(
    specialty: Optional[str] = None,
    provider: Optional[str] = None,
    patient_id: Optional[str] = None,
    preferred_date: Optional[str] = None,
    preferred_time: Optional[str] = None,
    reason: Optional[str] = None,
) -> ReferralOutput:
    """recommend healthcare providers for referrals.

use this tool when a user needs to be connected to a healthcare provider or needs information about where to receive care. the tool can find appropriate providers based on specialty and provide facility information.

important: always specify the 'specialty' parameter based on symptoms:
- cardiac/heart symptoms → 'cardiology'
- pregnancy/prenatal → 'obstetrics'
- children (age < 12) → 'pediatrics'
- general health concerns → 'general_practice'

use when: user agrees to or requests a referral to clinical care; user needs information about where to receive care.

do not use for: ordering commodities or medications; pharmacy refills or retail logistics; symptom triage or risk-level determination."""

    # find appropriate provider
    provider_info = find_provider_for_appointment(
        specialty=specialty,
        provider_name=provider,
    )

    if not provider_info:
        return ReferralOutput(
            status="error",
            message=f"no providers available for specialty: {specialty or 'general_practice'}",
        )

    # return provider recommendation
    return ReferralOutput(
        provider=provider_info.get("name"),
        specialty=provider_info.get("specialty"),
        facility=provider_info.get("facility"),
        date=preferred_date or "contact facility to schedule",
        time=preferred_time or "contact facility for availability",
        status="recommended",
        message=f"recommended provider: {provider_info.get('name')} at {provider_info.get('facility')}",
    )
