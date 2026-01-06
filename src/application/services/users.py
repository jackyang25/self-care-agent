"""user data retrieval service.

provides validated, typed access to user profile, history, and related data.
"""

from typing import Optional, List
import logging

from src.infrastructure.postgres.repositories.users import get_user_by_id as repo_get_user_by_id
from src.infrastructure.postgres.repositories.interactions import get_user_interactions as repo_get_user_interactions
from src.infrastructure.postgres.repositories.appointments import get_user_appointments as repo_get_user_appointments
from src.infrastructure.postgres.repositories.consents import get_user_consents as repo_get_user_consents
from src.infrastructure.postgres.repositories.providers import search_providers as repo_search_providers
from src.shared.schemas.services import (
    UserProfile,
    InteractionRecord,
    AppointmentRecord,
    ConsentRecord,
    ProviderRecord,
    UserCompleteHistory,
)

logger = logging.getLogger(__name__)


def get_user_profile(user_id: str) -> Optional[UserProfile]:
    """get user profile by id.
    
    args:
        user_id: user identifier
        
    returns:
        user profile or none if not found
    """
    user_data = repo_get_user_by_id(user_id)
    if not user_data:
        return None
    
    return UserProfile(**user_data)


def get_user_interaction_history(user_id: str, limit: int = 10) -> List[InteractionRecord]:
    """get user's interaction history.
    
    args:
        user_id: user identifier
        limit: maximum number of records
        
    returns:
        list of interaction records
    """
    interactions = repo_get_user_interactions(user_id, limit=limit)
    return [InteractionRecord(**i) for i in interactions]


def get_user_appointment_list(user_id: str, limit: int = 10) -> List[AppointmentRecord]:
    """get user's appointments.
    
    args:
        user_id: user identifier
        limit: maximum number of records
        
    returns:
        list of appointment records
    """
    appointments = repo_get_user_appointments(user_id, limit=limit)
    return [AppointmentRecord(**a) for a in appointments]


def get_user_consent_history(user_id: str, limit: int = 10) -> List[ConsentRecord]:
    """get user's consent history.
    
    args:
        user_id: user identifier
        limit: maximum number of records
        
    returns:
        list of consent records
    """
    consents = repo_get_user_consents(user_id, limit=limit)
    return [ConsentRecord(**c) for c in consents]


def get_user_complete_history(user_id: str, limit: int = 10) -> Optional[UserCompleteHistory]:
    """get complete user history including profile, interactions, and consents.
    
    args:
        user_id: user identifier
        limit: maximum records per category
        
    returns:
        complete user history or none if user not found
    """
    user = get_user_profile(user_id)
    if not user:
        return None
    
    interactions = get_user_interaction_history(user_id, limit=limit)
    consents = get_user_consent_history(user_id, limit=limit)
    
    return UserCompleteHistory(
        user=user,
        interactions=interactions,
        consents=consents,
    )


def get_available_providers(
    specialty: Optional[str] = None,
    country_context: Optional[str] = None,
    limit: int = 10,
) -> List[ProviderRecord]:
    """get available healthcare providers.
    
    args:
        specialty: filter by specialty
        country_context: filter by country
        limit: maximum number of records
        
    returns:
        list of provider records
    """
    providers = repo_search_providers(
        specialty=specialty,
        country_context=country_context,
        limit=limit,
    )
    return [ProviderRecord(**p) for p in providers]

