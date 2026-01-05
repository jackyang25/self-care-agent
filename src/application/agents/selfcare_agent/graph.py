"""langgraph graph construction."""

from typing import Any

from langgraph.graph import END, StateGraph

from src.application.agents.selfcare_agent.nodes import create_nodes
from src.application.agents.selfcare_agent.state import AgentState
from src.utils.logger import get_logger

logger = get_logger("agent.graph")


def create_agent_graph(llm_model: str, temperature: float) -> Any:
    """create a langgraph agent with tool calling and multi-step reasoning.

    the agent uses a state graph with conditional routing:
    - agent node: calls llm with system prompt and tool bindings
    - tools node: executes tool calls and returns results
    - loop continues until no more tool calls needed

    args:
        llm_model: openai model name (e.g., "gpt-4o")
        temperature: llm temperature (0.0-1.0)

    returns:
        compiled langgraph workflow
    """
    call_model, call_tools, should_continue, tool_node = create_nodes(
        llm_model, temperature
    )

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", call_tools)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent", should_continue, {"tools": "tools", "end": END}
    )
    workflow.add_edge("tools", "agent")

    logger.info(f"created agent graph: model={llm_model}, temperature={temperature}")
    return workflow.compile()

