"""provider referral service."""

from typing import Optional

from src.infrastructure.postgres.repositories.providers import find_provider_for_appointment
from src.shared.schemas.services import ReferralServiceOutput


def recommend_provider(
    specialty: Optional[str] = None,
    provider: Optional[str] = None,
    patient_id: Optional[str] = None,
    preferred_date: Optional[str] = None,
    preferred_time: Optional[str] = None,
    reason: Optional[str] = None,
) -> ReferralServiceOutput:
    """recommend a healthcare provider for referral.
    
    finds appropriate providers based on specialty and provides facility
    information for connecting patients to clinical care.
    
    specialty mapping:
    - cardiac/heart symptoms → 'cardiology'
    - pregnancy/prenatal → 'obstetrics'
    - children (age < 12) → 'pediatrics'
    - general health concerns → 'general_practice'
    
    args:
        specialty: medical specialty needed
        provider: preferred provider name
        patient_id: patient identifier
        preferred_date: preferred appointment date
        preferred_time: preferred appointment time
        reason: reason for referral
        
    returns:
        provider referral data
        
    raises:
        ValueError: if no providers available for specialty
    """
    # find appropriate provider
    provider_info = find_provider_for_appointment(
        specialty=specialty,
        provider_name=provider,
    )

    if not provider_info:
        raise ValueError(f"no providers available for specialty: {specialty or 'general_practice'}")

    # return provider recommendation
    return ReferralServiceOutput(
        provider=provider_info.get("name"),
        specialty=provider_info.get("specialty"),
        facility=provider_info.get("facility"),
        date=preferred_date or "contact facility to schedule",
        time=preferred_time or "contact facility for availability",
    )

