"""agent state definition for langgraph."""

from typing import TypedDict, Annotated, Sequence, List, Dict, Any
from operator import add
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """state for healthcare agent workflow.

    tracks conversation messages, config context, and system prompt.
    tool_outputs captures structured Pydantic outputs before stringification.
    sources specifically tracks RAG sources for UI display.
    """

    messages: Annotated[Sequence[BaseMessage], add_messages]
    config_context: dict  # request context payload for the current request
    system_prompt: str
    # structured tool outputs captured DURING tool execution
    tool_outputs: Annotated[List[Dict[str, Any]], add]
    # RAG sources extracted from knowledge base searches
    sources: Annotated[List[Dict[str, Any]], add]
