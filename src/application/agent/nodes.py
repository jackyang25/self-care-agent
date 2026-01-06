"""node functions for agent graph."""

from typing import Callable, Dict, List, Literal

from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from src.application.agent.prompt import SYSTEM_PROMPT
from src.application.agent.state import AgentState
from src.application.tools import TOOLS
from src.shared import context


def create_agent_node(llm_with_tools: ChatOpenAI) -> Callable[[AgentState], Dict[str, List[AIMessage]]]:
    """create agent reasoning node.
    
    args:
        llm_with_tools: llm with tools bound
        
    returns:
        node function
    """
    def agent_node(state: AgentState) -> Dict[str, List[AIMessage]]:
        """llm reasoning and planning."""

        system_prompt = state.get("system_prompt", SYSTEM_PROMPT)
        messages = [{"role": "system", "content": system_prompt}, *state["messages"]]
        response = llm_with_tools.invoke(messages)

        return {"messages": [response]}
    
    return agent_node


def create_execution_node(tool_node: ToolNode) -> Callable[[AgentState], Dict[str, List[ToolMessage]]]:
    """create tool execution node.
    
    args:
        tool_node: langgraph tool node
        
    returns:
        node function
    """
    def execution_node(state: AgentState) -> Dict[str, List[ToolMessage]]:
        """execute tool calls with user context.
        
        syncs user context from state to context vars before tool execution.
        this allows tools to access user data without explicit parameter passing.
        """
        
        # sync user context from state to context vars for tool access
        user_ctx = state.get("user_context")
        if user_ctx:
            if user_ctx.user_id:
                context.current_user_id.set(user_ctx.user_id)
            if user_ctx.age is not None:
                context.current_user_age.set(user_ctx.age)
            if user_ctx.gender:
                context.current_user_gender.set(user_ctx.gender)
            if user_ctx.timezone:
                context.current_user_timezone.set(user_ctx.timezone)
            if user_ctx.country:
                context.current_user_country.set(user_ctx.country)
        
        result = tool_node.invoke(state)
        return result
    
    return execution_node


def router(state: AgentState) -> Literal["tools", "end"]:
    """route to tools or end based on agent response."""
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "end"

