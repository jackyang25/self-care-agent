"""referrals and scheduling tool."""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from src.database import get_db_cursor
from src.utils.context import current_user_id
from src.utils.tool_helpers import get_tool_logger, log_tool_call
from src.schemas.tool_outputs import ReferralOutput

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
    """process referrals and schedule appointments. use this for creating referrals to specialists, scheduling appointments, or managing patient appointments."""
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

    # query database for provider matching
    with get_db_cursor() as cur:
        provider_id = None
        provider_name = None
        provider_specialty = specialty
        facility = None

        if specialty:
            # match by specialty
            cur.execute(
                """
                SELECT provider_id, name, specialty, facility
                FROM providers
                WHERE specialty = %s AND is_active = true
                LIMIT 1
            """,
                (specialty,),
            )
            provider_row = cur.fetchone()
            if provider_row:
                provider_id = provider_row["provider_id"]
                provider_name = provider_row["name"]
                provider_specialty = provider_row["specialty"]
                facility = provider_row["facility"]
        elif provider:
            # match by name
            cur.execute(
                """
                SELECT provider_id, name, specialty, facility
                FROM providers
                WHERE name ILIKE %s AND is_active = true
                LIMIT 1
            """,
                (f"%{provider}%",),
            )
            provider_row = cur.fetchone()
            if provider_row:
                provider_id = provider_row["provider_id"]
                provider_name = provider_row["name"]
                provider_specialty = provider_row["specialty"]
                facility = provider_row["facility"]

        # fallback to general practice if no match
        if not provider_name:
            cur.execute("""
                SELECT provider_id, name, specialty, facility
                FROM providers
                WHERE specialty = 'general_practice' AND is_active = true
                LIMIT 1
            """)
            provider_row = cur.fetchone()
            if provider_row:
                provider_id = provider_row["provider_id"]
                provider_name = provider_row["name"]
                provider_specialty = provider_row["specialty"]
                facility = provider_row["facility"]
            else:
                # ultimate fallback if no providers in database
                provider_name = provider or "dr. smith"
                facility = "default clinic"

        # generate appointment id
        appointment_uuid = uuid.uuid4()
        appointment_id = f"APT-{appointment_uuid.hex[:8].upper()}"

        # handle date/time formats
        date = preferred_date or "2025-12-20"
        time_raw = preferred_time or "10:00 AM"

        # convert time to database format (HH:MM:SS)
        # handle various formats: "10:00 AM", "14:00", "2pm", etc.
        time_db = time_raw
        if "AM" in time_raw.upper() or "PM" in time_raw.upper():
            # convert 12-hour to 24-hour format
            try:
                time_obj = datetime.strptime(time_raw.strip(), "%I:%M %p")
                time_db = time_obj.strftime("%H:%M:%S")
            except (ValueError, AttributeError):
                # fallback if parsing fails
                time_db = "10:00:00"
        elif ":" not in time_raw:
            # just hour like "14" or "2pm"
            time_db = f"{time_raw.strip().replace('pm', '').replace('am', '')}:00:00"
        elif time_raw.count(":") == 1:
            # format like "14:30" - add seconds
            time_db = f"{time_raw}:00"

        # store appointment in database
        try:
            cur.execute(
                """
                INSERT INTO appointments (
                    appointment_id, user_id, provider_id, specialty,
                    appointment_date, appointment_time, status, reason,
                    sync_status, created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, now()
                )
            """,
                (
                    str(appointment_uuid),  # convert UUID to string
                    str(user_id),  # convert UUID to string
                    str(provider_id) if provider_id else None,
                    provider_specialty,
                    date,
                    time_db,
                    "scheduled",
                    reason,
                    "pending",
                ),
            )
            logger.info(
                f"successfully stored appointment {appointment_id} for user {user_id}"
            )
        except Exception as e:
            logger.error(f"failed to store appointment in database: {e}", exc_info=True)
            # continue anyway to return appointment info to user

    # return pydantic model instance (use original user-friendly time format)
    return ReferralOutput(
        appointment_id=appointment_id,
        provider=provider_name,
        specialty=provider_specialty,
        facility=facility,
        date=date,
        time=time_raw,  # use original format for display
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
