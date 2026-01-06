"""user management service."""

from typing import Optional, Tuple

from src.infrastructure.postgres.repositories.users import get_user_demographics as _get_user_demographics
from src.shared.context import current_user_id, current_user_age, current_user_gender
from src.shared.logger import get_logger

logger = get_logger("users")


def get_user_demographics() -> Tuple[Optional[int], Optional[str]]:
    """get age and gender for current user.
    
    tries context first (set at login), falls back to database if needed.
    
    returns:
        tuple of (age, gender) or (None, None) if not available
    """
    # try context first (most common path)
    age = current_user_age.get()
    gender = current_user_gender.get()
    
    if age is not None and gender is not None:
        logger.debug(f"using cached user demographics: age={age}, gender={gender}")
        return age, gender
    
    # fallback: fetch from database if not in context
    user_id = current_user_id.get()
    if not user_id:
        logger.warning("no user_id in context, cannot fetch demographics")
        return None, None
    
    logger.info("demographics not in context, fetching from database")
    try:
        age, gender = _get_user_demographics(user_id)
        if age is not None or gender is not None:
            logger.info(
                f"fetched user demographics from database: age={age}, gender={gender}"
            )
        return age, gender
    except Exception as e:
        logger.error(f"error fetching user demographics: {e}")
        return None, None

