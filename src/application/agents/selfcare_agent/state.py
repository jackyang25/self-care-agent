"""agent state definition."""

from typing import Annotated, Optional, TypedDict


class AgentState(TypedDict, total=False):
    """state for the agent."""

    messages: Annotated[list, lambda x, y: x + y]
    system_prompt: Optional[str]
    user_id: Optional[str]

