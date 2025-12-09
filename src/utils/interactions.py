"""utilities for storing user interactions."""

import uuid
import json
from typing import Optional, List, Dict, Any
from langchain_core.messages import AIMessage, ToolMessage
from src.db import get_db_cursor
from src.utils.context import current_user_id


def save_interaction(
    user_input: str,
    channel: str = "streamlit",
    protocol_invoked: Optional[str] = None,
    protocol_version: Optional[str] = None,
    triage_result: Optional[Dict[str, Any]] = None,
    risk_level: Optional[str] = None,
    recommendations: Optional[List[str]] = None,
    tools_called: Optional[List[str]] = None,
    user_id: Optional[str] = None,
) -> Optional[str]:
    """save user interaction to database.
    
    args:
        user_input: the user's message/input
        channel: communication channel (default: "streamlit")
        protocol_invoked: protocol that was invoked (e.g., "triage")
        protocol_version: version of the protocol
        triage_result: triage assessment results (if triage was called)
        risk_level: risk level from triage (if applicable)
        recommendations: list of recommendations
        tools_called: list of tool names that were called
        user_id: user id (if not provided, uses context variable)
    
    returns:
        interaction_id if successful, None if failed or no user_id
    """
    # get user_id from context if not provided
    if not user_id:
        user_id = current_user_id.get()
    
    # don't save if no user_id (user not logged in)
    if not user_id:
        return None
    
    try:
        interaction_id = str(uuid.uuid4())
        
        # prepare input as jsonb
        input_data = {"text": user_input}
        if tools_called:
            input_data["tools_called"] = tools_called
        
        # prepare recommendations as jsonb
        recommendations_data = recommendations if recommendations else []
        
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO interactions (
                    interaction_id, user_id, channel, input,
                    protocol_invoked, protocol_version,
                    triage_result, risk_level, recommendations,
                    created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, now()
                )
            """, (
                interaction_id,
                user_id,
                channel,
                json.dumps(input_data),
                protocol_invoked,
                protocol_version,
                json.dumps(triage_result) if triage_result else None,
                risk_level,
                json.dumps(recommendations_data),
            ))
        
        return interaction_id
    
    except Exception as e:
        # log error but don't fail the request
        import logging
        logging.error(f"failed to save interaction: {e}")
        return None


def extract_tool_info_from_messages(messages: List) -> Dict[str, Any]:
    """extract tool call information from agent messages.
    
    args:
        messages: list of messages from agent execution
    
    returns:
        dict with protocol_invoked, tools_called, triage_result, risk_level, recommendations
    """
    protocol_invoked = None
    protocol_version = None
    tools_called = []
    triage_result = None
    risk_level = None
    recommendations = []
    
    for msg in messages:
        # check for tool calls (AIMessage with tool_calls)
        if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
            for tool_call in msg.tool_calls:
                tool_name = tool_call.get("name", "unknown")
                tools_called.append(tool_name)
                
                # check if triage was called
                if tool_name == "triage_and_risk_flagging":
                    protocol_invoked = "triage"
                    protocol_version = "1.0"
                    # extract triage args
                    args = tool_call.get("args", {})
                    if args.get("urgency"):
                        risk_level = args["urgency"].lower()
                    if args.get("symptoms"):
                        triage_result = {
                            "symptoms": args["symptoms"],
                            "urgency": args.get("urgency"),
                        }
        
        # check for tool results (ToolMessage)
        if isinstance(msg, ToolMessage) and hasattr(msg, "content"):
            content = msg.content
            
            # try to parse as json (structured response)
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    # extract triage results from structured json
                    if data.get("risk_level"):
                        risk_level = data["risk_level"].lower()
                    if data.get("recommendation"):
                        recommendations.append(data["recommendation"])
                    if data.get("symptoms") or data.get("urgency"):
                        triage_result = {
                            "symptoms": data.get("symptoms"),
                            "urgency": data.get("urgency"),
                        }
            except (json.JSONDecodeError, AttributeError):
                # fallback to string parsing for backward compatibility
                content_lower = content.lower()
                if "triage assessment completed" in content_lower:
                    # extract risk level
                    if "risk level:" in content_lower:
                        parts = content_lower.split("risk level:")
                        if len(parts) > 1:
                            risk_part = parts[1].split(".")[0].strip()
                            if risk_part in ["low", "medium", "high", "critical"]:
                                risk_level = risk_part
                    
                    # extract recommendation
                    if "recommendation:" in content_lower:
                        parts = content_lower.split("recommendation:")
                        if len(parts) > 1:
                            rec = parts[1].split(".")[0].strip()
                            if rec:
                                recommendations.append(rec)
    
    return {
        "protocol_invoked": protocol_invoked,
        "protocol_version": protocol_version,
        "tools_called": tools_called if tools_called else None,
        "triage_result": triage_result,
        "risk_level": risk_level,
        "recommendations": recommendations if recommendations else None,
    }

