"""appointment scheduling service."""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from src.infrastructure.postgres.repositories.providers import find_provider_for_appointment
from src.infrastructure.postgres.repositories.appointments import create_appointment
from src.shared.schemas.services import AppointmentServiceOutput
import logging

logger = logging.getLogger(__name__)


def parse_time_to_db_format(time_str: Optional[str]) -> str:
    """parse time string to database format (HH:MM:SS).
    
    args:
        time_str: time string in various formats (e.g., "10:00 AM", "14:30", "2:30 PM")
        
    returns:
        time in HH:MM:SS format (default: "10:00:00")
    """
    if not time_str or ":" not in time_str:
        return "10:00:00"
    
    try:
        # handle 12-hour format with AM/PM
        if "AM" in time_str.upper() or "PM" in time_str.upper():
            time_obj = datetime.strptime(time_str.strip().upper(), "%I:%M %p")
            return time_obj.strftime("%H:%M:%S")
        # handle 24-hour format
        else:
            # add seconds if not present
            return time_str if time_str.count(":") == 2 else f"{time_str}:00"
    except ValueError:
        logger.warning(f"failed to parse time '{time_str}', using default")
        return "10:00:00"


def schedule_appointment(
    user_id: str,
    specialty: Optional[str] = None,
    provider_name: Optional[str] = None,
    preferred_date: Optional[str] = None,
    preferred_time: Optional[str] = None,
    reason: Optional[str] = None,
) -> AppointmentServiceOutput:
    """schedule an appointment for a user.
    
    handles provider selection, appointment ID generation, date/time parsing,
    and database persistence.
    
    args:
        user_id: user uuid
        specialty: medical specialty (e.g., 'cardiology', 'general_practice')
        provider_name: preferred provider name (optional)
        preferred_date: appointment date in YYYY-MM-DD format
        preferred_time: appointment time (various formats supported)
        reason: reason for appointment
        
    returns:
        dict with appointment details including:
        - appointment_id
        - provider (name)
        - specialty
        - facility
        - date
        - time
        - reason
    """
    # find suitable provider
    provider_data = find_provider_for_appointment(
        specialty=specialty,
        provider_name=provider_name,
    )
    
    if provider_data:
        provider_id = provider_data["provider_id"]
        provider_display_name = provider_data["name"]
        provider_specialty = provider_data["specialty"]
        facility = provider_data["facility"]
    else:
        # fallback if no providers in database
        logger.warning(f"no provider found: specialty={specialty}, provider_name={provider_name}")
        provider_id = None
        provider_display_name = provider_name or "dr. smith"
        provider_specialty = specialty or "general_practice"
        facility = "default clinic"
    
    # generate appointment id
    appointment_uuid = uuid.uuid4()
    appointment_id = f"APT-{appointment_uuid.hex[:8].upper()}"
    
    # use user-provided date or default to 7 days from now
    date = preferred_date or (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    # parse and format times
    time_display = preferred_time or "10:00 AM"
    time_db = parse_time_to_db_format(preferred_time)
    
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
    
    if not success:
        logger.error(f"failed to store appointment in database: {appointment_id}")
    
    return AppointmentServiceOutput(
        appointment_id=appointment_id,
        provider=provider_display_name,
        specialty=provider_specialty,
        facility=facility,
        date=date,
        time=time_display,
        status="pending",
        confirmation_code=appointment_id[:8],
    )

