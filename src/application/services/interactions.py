"""utilities for storing user interactions."""

import uuid
import json
from typing import Optional, List, Dict, Any

from langchain_core.messages import AIMessage, ToolMessage

from src.infrastructure.postgres.repositories.interactions import insert_interaction
from src.shared.context import current_user_id
from src.shared.schemas.services import InteractionServiceOutput
import logging

logger = logging.getLogger(__name__)


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
) -> InteractionServiceOutput:
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
    if not user_id:
        user_id = current_user_id.get()

    if not user_id:
        return None

    try:
        interaction_id = str(uuid.uuid4())
        input_data = {"text": user_input}
        if tools_called:
            input_data["tools_called"] = tools_called

        recommendations_data = recommendations if recommendations else []

        success = insert_interaction(
            interaction_id=interaction_id,
            user_id=user_id,
            channel=channel,
            input_data=input_data,
            protocol_invoked=protocol_invoked,
            protocol_version=protocol_version,
            triage_result=triage_result,
            risk_level=risk_level,
            recommendations=recommendations_data,
        )

        return InteractionServiceOutput(
            interaction_id=interaction_id,
            success=success,
        )

    except Exception as e:
        logger.error(f"failed to save interaction: {e}", exc_info=True)
        return InteractionServiceOutput(
            interaction_id="",
            success=False,
        )


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

    # map tool names to protocol names
    tool_to_protocol = {
        "triage_and_risk_flagging": "triage",
        "commodity_orders_and_fulfillment": "commodity",
        "pharmacy_orders_and_fulfillment": "pharmacy",
        "referrals_and_scheduling": "referrals",
        "database_query": "database",
    }

    for msg in messages:
        if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
            for tool_call in msg.tool_calls:
                tool_name = tool_call.get("name", "unknown")
                tools_called.append(tool_name)

                if tool_name in tool_to_protocol:
                    protocol_invoked = tool_to_protocol[tool_name]
                    protocol_version = "1.0"

                if tool_name == "triage_and_risk_flagging":
                    args = tool_call.get("args", {})
                    if args.get("urgency"):
                        risk_level = args["urgency"].lower()
                    if args.get("symptoms"):
                        triage_result = {
                            "symptoms": args["symptoms"],
                            "urgency": args.get("urgency"),
                        }

        if isinstance(msg, ToolMessage) and hasattr(msg, "content"):
            content = msg.content

            try:
                data = json.loads(content)

                if isinstance(data, dict):
                    if data.get("risk_level"):
                        risk_level = data["risk_level"].lower()
                    if data.get("recommendation"):
                        recommendations.append(data["recommendation"])
                    if data.get("symptoms") or data.get("urgency"):
                        triage_result = {
                            "symptoms": data.get("symptoms"),
                            "urgency": data.get("urgency"),
                        }
            except (json.JSONDecodeError, TypeError) as e:
                content_preview = content[:200] if isinstance(content, str) else type(content)
                logger.error(f"tool returned invalid json: error={e} | content={content_preview}")
                continue

    return {
        "protocol_invoked": protocol_invoked,
        "protocol_version": protocol_version,
        "tools_called": tools_called if tools_called else None,
        "triage_result": triage_result,
        "risk_level": risk_level,
        "recommendations": recommendations if recommendations else None,
    }


def extract_rag_sources(messages: List) -> List[Dict[str, str]]:
    """extract rag sources from tool messages.

    args:
        messages: list of agent messages

    returns:
        list of source dicts with title, content_type, similarity
    """
    rag_tool_call_ids = []
    for msg in messages:
        if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
            for tool_call in msg.tool_calls:
                if tool_call.get("name") == "rag_retrieval":
                    tool_call_id = tool_call.get("id")
                    if tool_call_id:
                        rag_tool_call_ids.append(tool_call_id)

    sources = []
    for msg in messages:
        if isinstance(msg, ToolMessage):
            tool_call_id = getattr(msg, "tool_call_id", None)
            if tool_call_id in rag_tool_call_ids:
                try:
                    data = json.loads(msg.content)
                    if isinstance(data, dict) and "documents" in data:
                        for doc in data["documents"]:
                            sources.append(
                                {
                                    "title": doc.get("title", "Unknown"),
                                    "content_type": doc.get("content_type"),
                                    "similarity": doc.get("similarity", 0),
                                }
                            )
                except (json.JSONDecodeError, KeyError, AttributeError):
                    pass

    return sources
