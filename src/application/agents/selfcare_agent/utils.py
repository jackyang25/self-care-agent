"""utility functions for agent operations."""

import json
from typing import Any, Dict, List

from langchain_core.messages import AIMessage, ToolMessage


def extract_rag_sources(messages: List) -> List[Dict[str, Any]]:
    """extract rag sources from tool messages.

    args:
        messages: list of agent messages

    returns:
        list of source dicts with title, content_type, similarity
    """
    # find rag tool call ids
    rag_tool_call_ids = []
    for msg in messages:
        if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
            for tool_call in msg.tool_calls:
                if tool_call.get("name") == "rag_retrieval":
                    tool_call_id = tool_call.get("id")
                    if tool_call_id:
                        rag_tool_call_ids.append(tool_call_id)

    # extract sources from matching tool messages
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

