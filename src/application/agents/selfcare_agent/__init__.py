"""selfcare agent - modular langgraph agent for health triage and care coordination."""

from src.application.agents.selfcare_agent.agent import get_agent, process_message
from src.application.agents.selfcare_agent.config import AGENT_CONFIG, SYSTEM_PROMPT_DATA
from src.application.agents.selfcare_agent.graph import create_agent_graph
from src.application.agents.selfcare_agent.state import AgentState

__all__ = [
    # main API
    "get_agent",
    "process_message",
    # graph creation
    "create_agent_graph",
    # configuration
    "AGENT_CONFIG",
    "SYSTEM_PROMPT_DATA",
    # state
    "AgentState",
]

