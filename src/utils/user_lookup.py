"""utilities for user lookup during authentication."""

from typing import Optional, Dict, Any
from src.db import get_db_cursor
from src.utils.logger import get_logger

logger = get_logger("user_lookup")


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """look up user by email address.

    args:
        email: user email address

    returns:
        user dict if found, None otherwise
    """
    try:
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT user_id, fhir_patient_id, primary_channel, phone_e164, 
                       email, preferred_language, literacy_mode, country_context_id,
                       demographics, accessibility, created_at, updated_at
                FROM users
                WHERE email = %s AND is_deleted = false
                """,
                (email,),
            )
            user = cur.fetchone()
            if user:
                return dict(user)
            return None
    except Exception as e:
        logger.error(f"failed to lookup user by email: {e}", exc_info=True)
        return None


def get_user_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    """look up user by phone number.

    args:
        phone: user phone number in E.164 format

    returns:
        user dict if found, None otherwise
    """
    try:
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT user_id, fhir_patient_id, primary_channel, phone_e164, 
                       email, preferred_language, literacy_mode, country_context_id,
                       demographics, accessibility, created_at, updated_at
                FROM users
                WHERE phone_e164 = %s AND is_deleted = false
                """,
                (phone,),
            )
            user = cur.fetchone()
            if user:
                return dict(user)
            return None
    except Exception as e:
        logger.error(f"failed to lookup user by phone: {e}", exc_info=True)
        return None
