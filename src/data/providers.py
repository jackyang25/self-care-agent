"""provider data access functions."""

from typing import Optional, List, Dict, Any
from src.db import get_db_cursor


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
        with get_db_cursor() as cur:
            query = """
                SELECT 
                    provider_id,
                    name,
                    specialty,
                    facility,
                    available_days,
                    country_context_id,
                    contact_info
                FROM providers
                WHERE is_active = true
            """
            params = []

            if specialty:
                query += " AND specialty = %s"
                params.append(specialty)

            if name:
                query += " AND name ILIKE %s"
                params.append(f"%{name}%")

            if country_context:
                query += " AND country_context_id = %s"
                params.append(country_context)

            query += " ORDER BY specialty, name LIMIT %s"
            params.append(limit)

            cur.execute(query, tuple(params))
            results = cur.fetchall()
            return [dict(row) for row in results]
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
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT 
                    provider_id,
                    name,
                    specialty,
                    facility,
                    available_days,
                    country_context_id,
                    contact_info
                FROM providers
                WHERE provider_id = %s AND is_active = true
                """,
                (provider_id,),
            )
            result = cur.fetchone()
            return dict(result) if result else None
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
        with get_db_cursor() as cur:
            # try by specialty first
            if specialty:
                cur.execute(
                    """
                    SELECT provider_id, name, specialty, facility
                    FROM providers
                    WHERE specialty = %s AND is_active = true
                    LIMIT 1
                    """,
                    (specialty,),
                )
                result = cur.fetchone()
                if result:
                    return dict(result)

            # try by name
            if provider_name:
                cur.execute(
                    """
                    SELECT provider_id, name, specialty, facility
                    FROM providers
                    WHERE name ILIKE %s AND is_active = true
                    LIMIT 1
                    """,
                    (f"%{provider_name}%",),
                )
                result = cur.fetchone()
                if result:
                    return dict(result)

            # fallback to general practice
            cur.execute(
                """
                SELECT provider_id, name, specialty, facility
                FROM providers
                WHERE specialty = 'general_practice' AND is_active = true
                LIMIT 1
                """
            )
            result = cur.fetchone()
            if result:
                return dict(result)

            return None
    except Exception:
        return None
