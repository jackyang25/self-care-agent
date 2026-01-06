"""langgraph construction."""

from typing import Any

from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from src.application.agent.nodes import create_agent_node, create_execution_node, router
from src.application.agent.state import AgentState
from src.application.tools import TOOLS


def create_agent_graph(llm_model: str, temperature: float) -> Any:
    """create langgraph agent with tool calling and multi-step reasoning.

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
    # initialize llm and tools
    llm = ChatOpenAI(model=llm_model, temperature=temperature)
    llm_with_tools = llm.bind_tools(TOOLS)
    tool_node = ToolNode(TOOLS)

    # create node functions
    agent_node = create_agent_node(llm_with_tools)
    execution_node = create_execution_node(tool_node)

    # build graph
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", execution_node)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", router, {"tools": "tools", "end": END})
    workflow.add_edge("tools", "agent")

    return workflow.compile()
