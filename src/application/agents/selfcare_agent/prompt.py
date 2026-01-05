"""prompt building and patient context."""

from datetime import datetime
from typing import Optional

import pytz


def build_patient_context(
    age: Optional[int],
    gender: Optional[str],
    timezone: str,
    country: Optional[str] = None,
) -> str:
    """build patient context section for system prompt.

    args:
        age: patient age
        gender: patient gender
        timezone: patient timezone (e.g., "America/New_York")
        country: patient country context (e.g., "za", "ke", "us")

    returns:
        formatted context string to append to system prompt
    """
    context_parts = []

    # add current time in user's timezone
    try:
        tz = pytz.timezone(timezone) if timezone else pytz.UTC
        current_time = datetime.now(tz)
        time_str = current_time.strftime("%A, %B %d, %Y at %I:%M %p %Z")
    except Exception:
        current_time = datetime.now(pytz.UTC)
        time_str = current_time.strftime("%A, %B %d, %Y at %I:%M %p UTC")

    context_parts.append(f"Current time: {time_str}")

    if age is not None:
        context_parts.append(f"Age: {age}")
    if gender is not None:
        context_parts.append(f"Gender: {gender}")
    if country is not None:
        context_parts.append(f"Country: {country}")

    if not context_parts:
        return ""

    context_lines = "\n".join(f"- {part}" for part in context_parts)
    return (
        f"\n\n## current patient context\n\n{context_lines}\n\n"
        f"use this information to provide appropriate, personalized care. "
        f"use the current time to schedule appointments appropriately "
        f"(e.g., 'tomorrow' means the next day from current time). "
        f"when using rag_retrieval, country-specific clinical guidelines will be prioritized."
    )

