"""user data access functions."""

from typing import Optional, Dict, Any
from src.infrastructure.persistence.postgres.connection import get_db_cursor


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """get user by email address.

    args:
        email: user email address

    returns:
        user dict with all fields, or None if not found
    """
    try:
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT user_id, fhir_patient_id, primary_channel, phone_e164, 
                       email, preferred_language, literacy_mode, country_context_id,
                       demographics, accessibility, timezone, created_at, updated_at
                FROM users
                WHERE email = %s AND is_deleted = false
                """,
                (email,),
            )
            result = cur.fetchone()
            return dict(result) if result else None
    except Exception:
        return None


def get_user_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    """get user by phone number (e164 format).

    args:
        phone: phone number in e164 format (e.g., +1234567890)

    returns:
        user dict with all fields, or None if not found
    """
    try:
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT user_id, fhir_patient_id, primary_channel, phone_e164, 
                       email, preferred_language, literacy_mode, country_context_id,
                       demographics, accessibility, timezone, created_at, updated_at
                FROM users
                WHERE phone_e164 = %s AND is_deleted = false
                """,
                (phone,),
            )
            result = cur.fetchone()
            return dict(result) if result else None
    except Exception:
        return None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """get user by user_id.

    args:
        user_id: user uuid

    returns:
        user dict with all fields, or None if not found
    """
    try:
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT user_id, fhir_patient_id, primary_channel, phone_e164, 
                       email, preferred_language, literacy_mode, country_context_id,
                       demographics, accessibility, timezone, created_at, updated_at
                FROM users
                WHERE user_id = %s AND is_deleted = false
                """,
                (user_id,),
            )
            result = cur.fetchone()
            return dict(result) if result else None
    except Exception:
        return None


def get_user_demographics(user_id: str) -> tuple[Optional[int], Optional[str]]:
    """get user age and gender from demographics.

    args:
        user_id: user uuid

    returns:
        tuple of (age, gender) or (None, None) if not found
    """
    try:
        with get_db_cursor() as cur:
            cur.execute("SELECT demographics FROM users WHERE user_id = %s", (user_id,))
            result = cur.fetchone()
            if result and result["demographics"]:
                demographics = result["demographics"]
                age = demographics.get("age")
                gender = demographics.get("gender")
                return age, gender
    except Exception:
        pass
    return None, None

