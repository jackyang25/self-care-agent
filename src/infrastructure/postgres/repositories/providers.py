"""provider data access functions using ORM."""

from typing import Optional, List, Dict, Any
from src.infrastructure.postgres.connection import get_db_session
from src.infrastructure.postgres.models import Provider


def search_providers(
    specialty: Optional[str] = None,
    name: Optional[str] = None,
    country_context: Optional[str] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """search for healthcare providers with optional filters.

    args:
        specialty: filter by specialty (e.g., 'cardiology', 'pediatrics')
        name: search by provider name (partial match, case-insensitive)
        country_context: filter by country context id
        limit: maximum number of results

    returns:
        list of provider dicts matching criteria
    """
    try:
        with get_db_session() as session:
            query = session.query(Provider).filter(Provider.is_active == True)
            
            if specialty:
                query = query.filter(Provider.specialty == specialty)
            
            if name:
                query = query.filter(Provider.name.ilike(f"%{name}%"))
            
            if country_context:
                query = query.filter(Provider.country_context_id == country_context)
            
            providers = (
                query.order_by(Provider.specialty, Provider.name)
                .limit(limit)
                .all()
            )
            
            return [provider.to_dict() for provider in providers]
    except Exception:
        return []


def get_provider_by_id(provider_id: str) -> Optional[Dict[str, Any]]:
    """get provider by provider_id.

    args:
        provider_id: provider uuid

    returns:
        provider dict or None if not found
    """
    try:
        with get_db_session() as session:
            provider = session.query(Provider).filter(
                Provider.provider_id == provider_id,
                Provider.is_active == True
            ).first()
            return provider.to_dict() if provider else None
    except Exception:
        return None


def find_provider_for_appointment(
    specialty: Optional[str] = None,
    provider_name: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """find a suitable provider for appointment booking.

    searches by specialty or name, with fallback to general practice.

    args:
        specialty: preferred specialty
        provider_name: preferred provider name

    returns:
        provider dict or None if no providers available
    """
    try:
        with get_db_session() as session:
            # try by specialty first
            if specialty:
                provider = session.query(Provider).filter(
                    Provider.specialty == specialty,
                    Provider.is_active == True
                ).first()
                if provider:
                    return {
                        "provider_id": str(provider.provider_id),
                        "name": provider.name,
                        "specialty": provider.specialty,
                        "facility": provider.facility,
                    }
            
            # try by name
            if provider_name:
                provider = session.query(Provider).filter(
                    Provider.name.ilike(f"%{provider_name}%"),
                    Provider.is_active == True
                ).first()
                if provider:
                    return {
                        "provider_id": str(provider.provider_id),
                        "name": provider.name,
                        "specialty": provider.specialty,
                        "facility": provider.facility,
                    }
            
            # fallback to general practice
            provider = session.query(Provider).filter(
                Provider.specialty == "general_practice",
                Provider.is_active == True
            ).first()
            if provider:
                return {
                    "provider_id": str(provider.provider_id),
                    "name": provider.name,
                    "specialty": provider.specialty,
                    "facility": provider.facility,
                }
            
            return None
    except Exception:
        return None
