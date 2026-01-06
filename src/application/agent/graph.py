"""langgraph state, nodes, and graph construction."""

from typing import Annotated, Dict, List, Literal, Optional, TypedDict

from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from src.application.agent.config import PROMPT_DATA
from src.application.tools import TOOLS
from src.shared.logger import get_logger

logger = get_logger("agent.graph")


# -----------------------------------------------------------------------------
# State
# -----------------------------------------------------------------------------


class AgentState(TypedDict, total=False):
    """state for the agent."""

    messages: Annotated[list, lambda x, y: x + y]
    system_prompt: Optional[str]
    user_id: Optional[str]


# -----------------------------------------------------------------------------
# Nodes
# -----------------------------------------------------------------------------


def _create_nodes(llm_model: str, temperature: float) -> tuple:
    """create langgraph nodes for the agent.

    args:
        llm_model: openai model name
        temperature: llm temperature

    returns:
        tuple of (call_model_fn, call_tools_fn, should_continue_fn, tool_node)
    """
    llm = ChatOpenAI(model=llm_model, temperature=temperature)
    llm_with_tools = llm.bind_tools(TOOLS)
    tool_node = ToolNode(TOOLS)

    def should_continue(state: AgentState) -> Literal["tools", "end"]:
        """route to tools if llm made tool calls, otherwise end."""
        last_message = state["messages"][-1]
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "tools"
        return "end"

    def call_model(state: AgentState) -> Dict[str, List[AIMessage]]:
        """invoke llm with system prompt and conversation history."""
        system_prompt = state.get("system_prompt", PROMPT_DATA["prompt"])
        messages = [{"role": "system", "content": system_prompt}, *state["messages"]]
        response = llm_with_tools.invoke(messages)

        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                logger.info(
                    f"tool call: {tool_call.get('name', 'unknown')} "
                    f"args={tool_call.get('args', {})}"
                )

        return {"messages": [response]}

    def call_tools(state: AgentState) -> Dict[str, List[ToolMessage]]:
        """execute tool calls and return results."""
        result = tool_node.invoke(state)

        if isinstance(result, dict) and "messages" in result:
            for msg in result["messages"]:
                if isinstance(msg, ToolMessage):
                    logger.info(f"tool result: {msg.content[:200]}...")

        return result

    return call_model, call_tools, should_continue, tool_node


# -----------------------------------------------------------------------------
# Graph
# -----------------------------------------------------------------------------


def create_agent_graph(llm_model: str, temperature: float):
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
    call_model, call_tools, should_continue, _ = _create_nodes(llm_model, temperature)

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
