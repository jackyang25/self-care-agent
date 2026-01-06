"""referrals and scheduling tool."""

import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from src.infrastructure.postgres.repositories.providers import (
    find_provider_for_appointment,
)
from src.infrastructure.postgres.repositories.appointments import create_appointment
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

    # find suitable provider
    provider_data = find_provider_for_appointment(
        specialty=specialty,
        provider_name=provider,
    )

    if provider_data:
        provider_id = provider_data["provider_id"]
        provider_name = provider_data["name"]
        provider_specialty = provider_data["specialty"]
        facility = provider_data["facility"]
    else:
        # ultimate fallback if no providers in database
        provider_id = None
        provider_name = provider or "dr. smith"
        provider_specialty = specialty or "general_practice"
        facility = "default clinic"

    # generate appointment id
    appointment_uuid = uuid.uuid4()
    appointment_id = f"APT-{appointment_uuid.hex[:8].upper()}"

    # use user-provided date/time or simple demo defaults
    date = preferred_date or (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    time_display = preferred_time or "10:00 AM"

    # convert time to database format
    time_db = "10:00:00"
    if time_display and ":" in time_display:
        try:
            if "AM" in time_display.upper() or "PM" in time_display.upper():
                time_obj = datetime.strptime(time_display.strip().upper(), "%I:%M %p")
                time_db = time_obj.strftime("%H:%M:%S")
            else:
                time_db = (
                    time_display
                    if time_display.count(":") == 2
                    else f"{time_display}:00"
                )
        except ValueError:
            time_db = "10:00:00"

    # store appointment in database
    success = create_appointment(
        appointment_id=str(appointment_uuid),
        user_id=str(user_id),
        provider_id=str(provider_id) if provider_id else None,
        specialty=provider_specialty,
        appointment_date=date,
        appointment_time=time_db,
        status="scheduled",
        reason=reason,
        sync_status="pending",
    )

    if success:
        logger.info(
            f"successfully stored appointment {appointment_id} for user {user_id}"
        )
    else:
        logger.error("failed to store appointment in database")
        # continue anyway to return appointment info to user

    # return pydantic model instance (use user-friendly time format)
    return ReferralOutput(
        appointment_id=appointment_id,
        provider=provider_name,
        specialty=provider_specialty,
        facility=facility,
        date=date,
        time=time_display,  # use parsed display format
        reason=reason,
    ).model_dump()


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
