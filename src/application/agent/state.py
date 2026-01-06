"""langgraph state definition for agent."""

from typing import Annotated, Optional, TypedDict

from src.shared.context import UserContext


class AgentState(TypedDict, total=False):
    """state for the agent.
    
    all user-specific data flows through user_context for explicit state management.
    """

    messages: Annotated[list, lambda x, y: x + y]
    system_prompt: Optional[str]
    user_context: Optional[UserContext]

