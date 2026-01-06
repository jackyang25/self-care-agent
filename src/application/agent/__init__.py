"""selfcare agent - modular langgraph agent for health triage and care coordination."""

from src.application.agent.config import AGENT_CONFIG, PROMPT_DATA, build_patient_context
from src.application.agent.graph import AgentState, create_agent_graph
from src.application.agent.runtime import get_agent, process_message

__all__ = [
    # main API
    "get_agent",
    "process_message",
    # graph creation
    "create_agent_graph",
    # configuration
    "AGENT_CONFIG",
    "PROMPT_DATA",
    "build_patient_context",
    # state
    "AgentState",
]
