"""referrals and scheduling tool."""

from typing import Optional
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from src.utils.logger import get_logger

logger = get_logger("referrals")


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
) -> str:
    """process referrals and schedule appointments. use this for creating referrals to specialists, scheduling appointments, or managing patient appointments."""
    logger.info("referrals_and_scheduling called")
    logger.debug(
        f"arguments: specialty={specialty}, provider={provider}, patient_id={patient_id}, preferred_date={preferred_date}, preferred_time={preferred_time}, reason={reason}"
    )

    appointment_id = "APT-11111"
    provider_name = provider or "dr. smith"
    date = preferred_date or "2025-12-15"
    time = preferred_time or "10:00 AM"

    return f"appointment scheduled successfully. appointment_id: {appointment_id}, provider: {provider_name}, date: {date}, time: {time}. status: success"


referral_tool = StructuredTool.from_function(
    func=referrals_and_scheduling,
    name="referrals_and_scheduling",
    description="""create referrals and schedule clinical appointments.

use this tool when a user needs to be connected to a healthcare provider, book a clinic or telemedicine appointment, or follow up on a referral. the tool can generate structured referral information, confirm appointment times, and coordinate next steps with clinical partners.

use when: user agrees to or requests a referral to clinical care; user wants to book, reschedule, or confirm an appointment; user needs information about where and when to receive care.

do not use for: ordering commodities or medications; pharmacy refills or retail logistics; symptom triage or risk-level determination.""",
    args_schema=ReferralInput,
)
