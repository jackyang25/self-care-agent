"""langgraph nodes for the agent."""

from typing import Dict, List, Literal

from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from src.application.agents.selfcare_agent.config import SYSTEM_PROMPT_DATA
from src.application.agents.selfcare_agent.state import AgentState
from src.application.tools import TOOLS
from src.utils.logger import get_logger

logger = get_logger("agent.nodes")


def create_nodes(llm_model: str, temperature: float) -> tuple:
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
        system_prompt = state.get("system_prompt", SYSTEM_PROMPT_DATA["prompt"])
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

