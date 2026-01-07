"""agent state definition for langgraph."""

from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """state for healthcare agent workflow.
    
    tracks conversation messages, config context, and system prompt.
    """
    
    messages: Annotated[Sequence[BaseMessage], add_messages]
    config_context: dict  # age, gender, timezone, country from config
    system_prompt: str
