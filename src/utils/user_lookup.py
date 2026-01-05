"""utilities for user lookup during authentication."""

from typing import Optional, Dict, Any
from src.infrastructure.persistence.postgres.repositories.users import get_user_by_email as _get_user_by_email, get_user_by_phone as _get_user_by_phone
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
        return _get_user_by_email(email)
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
        return _get_user_by_phone(phone)
    except Exception as e:
        logger.error(f"failed to lookup user by phone: {e}", exc_info=True)
        return None
