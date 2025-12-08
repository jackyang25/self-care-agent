"""database query tool for agent."""

from typing import Optional
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from src.db import get_db_cursor
from src.utils.context import current_user_id


class DatabaseQueryInput(BaseModel):
    """input schema for database queries."""

    query_type: str = Field(
        description="type of query: 'get_user_by_id', 'get_user_by_email', 'get_user_by_phone', 'get_user_history', 'get_user_interactions'"
    )
    user_id: Optional[str] = Field(
        None, description="user id (uuid) - use for 'get_user_by_id' or 'get_user_history'"
    )
    email: Optional[str] = Field(
        None, description="user email - use for 'get_user_by_email'"
    )
    phone: Optional[str] = Field(
        None, description="user phone number (e164 format) - use for 'get_user_by_phone'"
    )
    limit: Optional[int] = Field(
        10, description="maximum number of results to return (default: 10)"
    )


def database_query(
    query_type: str,
    user_id: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    limit: Optional[int] = 10,
) -> str:
    """retrieve user data from the database.
    
    use this tool to:
    - find user by email, phone, or user_id
    - get user profile information
    - get user's interaction history
    - get complete user history (profile + interactions + consents)
    
    note: if user_id is not provided and query requires it, the tool will automatically
    use the current user's id from session context.
    """
    # automatically use current user_id from context if not provided
    if not user_id:
        user_id = current_user_id.get()
    
    print(f"[TOOL CALLED] database_query")
    print(f"[ARGUMENTS] query_type={query_type}, user_id={user_id}, email={email}, phone={phone}, limit={limit}")

    try:
        with get_db_cursor() as cur:
            # find user by email
            if query_type == "get_user_by_email":
                if not email:
                    return "error: email is required for get_user_by_email"
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
                    return f"user found: {dict(user)}"
                else:
                    return f"user not found for email: {email}"

            # find user by phone
            elif query_type == "get_user_by_phone":
                if not phone:
                    return "error: phone is required for get_user_by_phone"
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
                    return f"user found: {dict(user)}"
                else:
                    return f"user not found for phone: {phone}"

            # get user by user_id
            elif query_type == "get_user_by_id":
                if not user_id:
                    return "error: user_id is required for get_user_by_id"
                cur.execute(
                    """
                    SELECT user_id, fhir_patient_id, primary_channel, phone_e164, 
                           email, preferred_language, literacy_mode, country_context_id,
                           demographics, accessibility, created_at, updated_at
                    FROM users
                    WHERE user_id = %s AND is_deleted = false
                    """,
                    (user_id,),
                )
                user = cur.fetchone()
                if user:
                    return f"user found: {dict(user)}"
                else:
                    return f"user not found for user_id: {user_id}"

            # get user interactions
            elif query_type == "get_user_interactions":
                if not user_id:
                    return "error: user_id is required for get_user_interactions"
                cur.execute(
                    """
                    SELECT interaction_id, channel, input, protocol_invoked,
                           triage_result, risk_level, recommendations,
                           follow_up_at, created_at
                    FROM interactions
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (user_id, limit),
                )
                interactions = cur.fetchall()
                if interactions:
                    return f"found {len(interactions)} interaction(s): {[dict(i) for i in interactions]}"
                else:
                    return f"no interactions found for user_id: {user_id}"

            # get complete user history (profile + interactions + consents)
            elif query_type == "get_user_history":
                if not user_id:
                    return "error: user_id is required for get_user_history"
                
                # get user profile
                cur.execute(
                    """
                    SELECT user_id, fhir_patient_id, primary_channel, phone_e164, 
                           email, preferred_language, literacy_mode, country_context_id,
                           demographics, accessibility, created_at, updated_at
                    FROM users
                    WHERE user_id = %s AND is_deleted = false
                    """,
                    (user_id,),
                )
                user = cur.fetchone()
                
                if not user:
                    return f"user not found for user_id: {user_id}"
                
                # get interactions
                cur.execute(
                    """
                    SELECT interaction_id, channel, input, protocol_invoked,
                           triage_result, risk_level, recommendations,
                           follow_up_at, created_at
                    FROM interactions
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (user_id, limit),
                )
                interactions = cur.fetchall()
                
                # get consents
                cur.execute(
                    """
                    SELECT consent_id, scope, status, version,
                           jurisdiction, evidence, recorded_at
                    FROM consents
                    WHERE user_id = %s
                    ORDER BY recorded_at DESC
                    LIMIT %s
                    """,
                    (user_id, limit),
                )
                consents = cur.fetchall()
                
                result = {
                    "user": dict(user),
                    "interactions": [dict(i) for i in interactions],
                    "consents": [dict(c) for c in consents],
                }
                return f"user history: {result}"

            else:
                return f"error: unknown query_type '{query_type}'. valid types: get_user_by_id, get_user_by_email, get_user_by_phone, get_user_interactions, get_user_history"

    except Exception as e:
        return f"database query error: {str(e)}"


database_tool = StructuredTool.from_function(
    func=database_query,
    name="database_query",
    description="""retrieve user data from the database.

use this tool when:
- user provides their email, phone number, or user_id and you need to look up their information
- you need to access a user's profile, interaction history, or complete medical history
- you need to check past interactions, triage results, or consent records for a user

query types:
- 'get_user_by_email': find user by email address
- 'get_user_by_phone': find user by phone number (e164 format like +1234567890)
- 'get_user_by_id': retrieve user profile by user_id (uuid)
- 'get_user_interactions': get interaction history for a user (ordered by most recent)
- 'get_user_history': get complete user history including profile, interactions, and consents

examples:
- user says "my email is user@example.com" → use get_user_by_email
- user says "my phone is +1234567890" → use get_user_by_phone
- you have a user_id and need full history → use get_user_history

do not use for: creating new records, updating data, or deleting records.""",
    args_schema=DatabaseQueryInput,
)

