"""interaction data access functions."""

import json
from typing import Optional, List, Dict, Any
from src.db import get_db_cursor


def insert_interaction(
    interaction_id: str,
    user_id: str,
    channel: str,
    input_data: Dict[str, Any],
    protocol_invoked: Optional[str] = None,
    protocol_version: Optional[str] = None,
    triage_result: Optional[Dict[str, Any]] = None,
    risk_level: Optional[str] = None,
    recommendations: Optional[List[str]] = None,
) -> bool:
    """insert interaction record into database.

    args:
        interaction_id: unique interaction id
        user_id: user uuid
        channel: communication channel
        input_data: user input as dict
        protocol_invoked: protocol name
        protocol_version: protocol version
        triage_result: triage results dict
        risk_level: risk level string
        recommendations: list of recommendations

    returns:
        True if successful, False otherwise
    """
    try:
        with get_db_cursor() as cur:
            cur.execute(
                """
                INSERT INTO interactions (
                    interaction_id, user_id, channel, input,
                    protocol_invoked, protocol_version,
                    triage_result, risk_level, recommendations,
                    created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, now()
                )
                """,
                (
                    interaction_id,
                    user_id,
                    channel,
                    json.dumps(input_data),
                    protocol_invoked,
                    protocol_version,
                    json.dumps(triage_result) if triage_result else None,
                    risk_level,
                    json.dumps(recommendations) if recommendations else None,
                ),
            )
            return True
    except Exception:
        return False


def get_user_interactions(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """get interaction history for a user.

    args:
        user_id: user uuid
        limit: maximum number of results

    returns:
        list of interaction dicts
    """
    try:
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT 
                    interaction_id,
                    user_id,
                    channel,
                    input,
                    protocol_invoked,
                    protocol_version,
                    triage_result,
                    risk_level,
                    recommendations,
                    created_at
                FROM interactions
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (user_id, limit),
            )
            results = cur.fetchall()
            return [dict(row) for row in results]
    except Exception:
        return []
