"""langgraph agent with native tool calling."""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from src.tools import TOOLS
from src.logger import get_logger

logger = get_logger("agent")


class AgentState(TypedDict):
    """state for the agent."""

    messages: Annotated[list, lambda x, y: x + y]


def create_agent(llm_model: str = "gpt-3.5-turbo", temperature: float = 0.7):
    """create a langgraph agent with native tool calling."""
    llm = ChatOpenAI(model=llm_model, temperature=temperature)
    llm_with_tools = llm.bind_tools(TOOLS)

    tool_node = ToolNode(TOOLS)

    def should_continue(state: AgentState):
        """determine if we should continue or end."""
        messages = state["messages"]
        last_message = messages[-1]

        if last_message.tool_calls:
            return "tools"
        return "end"

    def call_model(state: AgentState):
        """call the llm with tools."""
        messages = state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END,
        },
    )

    workflow.add_edge("tools", "agent")

    # above is a loop that will continue to call the agent until the end is reached
    # multi-step reasoning
    # tool chaining 
    # error correction (If a tool result is insufficient, the model may call it again with new params)
    # safety checks (The agent can inject guardrails between tool calls)

    return workflow.compile()


def process_message(agent, user_input: str):
    """process a user message through the agent."""
    state = {"messages": [HumanMessage(content=user_input)]}
    result = agent.invoke(state)

    messages = result["messages"]
    last_message = messages[-1]

    # find tool execution info in message chain
    tool_info = []
    for i, msg in enumerate(messages):
        if isinstance(msg, ToolMessage):
            logger.info(f"tool result: {msg.content[:200]}")
            tool_info.append("tool executed")
        elif (
            isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls
        ):
            for tool_call in msg.tool_calls:
                tool_name = tool_call.get("name", "unknown")
                tool_args = tool_call.get("args", {})
                logger.info(f"calling tool: {tool_name} with args: {tool_args}")
                tool_info.append(f"tool: {tool_name}")

    if isinstance(last_message, AIMessage):
        if last_message.content:
            response = last_message.content
            if tool_info:
                response = f"{response}\n\n[tool execution: {', '.join(tool_info)}]"
            return response
        elif hasattr(last_message, "tool_calls") and last_message.tool_calls:
            tool_name = last_message.tool_calls[0].get("name", "unknown")
            return f"tool '{tool_name}' executed successfully"

    return "processed"
