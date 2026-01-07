"""provider referral tool."""

from typing import Optional

from langchain_core.tools import tool

from src.application.services.referrals import recommend_provider
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

    try:
        # call service layer
        result = recommend_provider(
            specialty=specialty,
            provider=provider,
            patient_id=patient_id,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            reason=reason,
        )
        
        # transform service output to tool output (add presentation layer)
        return ReferralOutput(
            status="recommended",
            message=f"recommended provider: {result.provider} at {result.facility}",
            provider=result.provider,
            specialty=result.specialty,
            facility=result.facility,
            date=result.date,
            time=result.time,
            reason=reason,
        )
    
    except ValueError as e:
        return ReferralOutput(
            status="error",
            message=str(e),
        )
    
    except Exception as e:
        return ReferralOutput(
            status="error",
            message=f"referral failed: {str(e)}",
        )
