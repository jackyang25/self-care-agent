"""referrals and scheduling tool."""

from typing import Optional, Dict, Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from src.application.services.appointments import schedule_appointment
from src.shared.context import current_user_id
from src.shared.logger import get_tool_logger, log_tool_call
from src.shared.schemas.tools import ReferralOutput

logger = get_tool_logger("referrals")


class ReferralInput(BaseModel):
    """input schema for referrals and scheduling."""

    specialty: Optional[str] = Field(
        None, description="medical specialty or department"
    )
    provider: Optional[str] = Field(None, description="preferred provider name")
    patient_id: Optional[str] = Field(None, description="patient identifier")
    preferred_date: Optional[str] = Field(
        None, description="preferred appointment date"
    )
    preferred_time: Optional[str] = Field(
        None, description="preferred appointment time"
    )
    reason: Optional[str] = Field(
        None, description="reason for referral or appointment"
    )


def referrals_and_scheduling(
    specialty: Optional[str] = None,
    provider: Optional[str] = None,
    patient_id: Optional[str] = None,
    preferred_date: Optional[str] = None,
    preferred_time: Optional[str] = None,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """process referrals and schedule appointments.

    args:
        specialty: medical specialty or department
        provider: preferred provider name
        patient_id: patient identifier
        preferred_date: preferred appointment date
        preferred_time: preferred appointment time
        reason: reason for referral or appointment

    returns:
        dict with appointment confirmation details
    """
    log_tool_call(
        logger,
        "referrals_and_scheduling",
        specialty=specialty,
        provider=provider,
        patient_id=patient_id,
        preferred_date=preferred_date,
        preferred_time=preferred_time,
        reason=reason,
    )

    user_id = current_user_id.get()
    if not user_id:
        logger.error("no user_id in context - appointment cannot be saved")
        return {
            "status": "error",
            "message": "no user logged in. please log in to schedule appointments.",
        }

    # schedule appointment using service layer
    appointment_data = schedule_appointment(
        user_id=user_id,
        specialty=specialty,
        provider_name=provider,
        preferred_date=preferred_date,
        preferred_time=preferred_time,
        reason=reason,
    )

    # return pydantic model instance
    return ReferralOutput(**appointment_data).model_dump()


referral_tool = StructuredTool.from_function(
    func=referrals_and_scheduling,
    name="referrals_and_scheduling",
    description="""create referrals and schedule clinical appointments.

use this tool when a user needs to be connected to a healthcare provider, book a clinic or telemedicine appointment, or follow up on a referral. the tool can generate structured referral information, confirm appointment times, and coordinate next steps with clinical partners.

important: always specify the 'specialty' parameter based on symptoms:
- cardiac/heart symptoms → 'cardiology'
- pregnancy/prenatal → 'obstetrics'
- children (age < 12) → 'pediatrics'
- general health concerns → 'general_practice'

use when: user agrees to or requests a referral to clinical care; user wants to book, reschedule, or confirm an appointment; user needs information about where and when to receive care.

do not use for: ordering commodities or medications; pharmacy refills or retail logistics; symptom triage or risk-level determination.""",
    args_schema=ReferralInput,
)
