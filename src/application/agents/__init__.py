"""agents - orchestrators that coordinate tools and services."""

from src.application.agents.selfcare_agent import (
    create_agent_graph,
    get_agent,
    process_message,
)

# backward compatibility alias
create_agent = create_agent_graph

__all__ = ["create_agent", "create_agent_graph", "get_agent", "process_message"]

