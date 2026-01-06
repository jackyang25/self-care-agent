"""consent data access functions."""

from typing import List, Dict, Any
from src.infrastructure.postgres.connection import get_db_cursor


def get_user_consents(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """get consent records for a user.

    args:
        user_id: user uuid
        limit: maximum number of results

    returns:
        list of consent dicts
    """
    try:
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT 
                    consent_id,
                    user_id,
                    scope,
                    status,
                    version,
                    jurisdiction,
                    evidence,
                    recorded_at
                FROM consents
                WHERE user_id = %s
                ORDER BY recorded_at DESC
                LIMIT %s
                """,
                (user_id, limit),
            )
            results = cur.fetchall()
            return [dict(row) for row in results]
    except Exception:
        return []

