"""node functions for agent graph."""

from typing import Callable, Dict, List, Literal

from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from src.application.agent.prompt import SYSTEM_PROMPT
from src.application.agent.state import AgentState
from src.application.tools import TOOLS


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
        """execute tool calls.
        
        tools receive context directly as parameters.
        no implicit state - all data flows explicitly through tool parameters.
        """
        
        # get context from state
        config_ctx = state.get("config_context")
        
        # inject context into tool calls
        if config_ctx:
            # get the last AI message with tool calls
            messages = state.get("messages", [])
            for msg in reversed(messages):
                if isinstance(msg, AIMessage) and msg.tool_calls:
                    # inject age, gender, country into tool calls that need them
                    for tool_call in msg.tool_calls:
                        tool_name = tool_call.get("name", "")
                        args = tool_call.get("args", {})
                        
                        # inject context for tools that use it
                        if tool_name == "clinical_triage":
                            if "age" not in args and config_ctx.get("age"):
                                args["age"] = config_ctx["age"]
                            if "gender" not in args and config_ctx.get("gender"):
                                args["gender"] = config_ctx["gender"]
                        
                        elif tool_name == "rag_knowledge_base":
                            if "country" not in args and config_ctx.get("country"):
                                args["country"] = config_ctx["country"]
        
        result = tool_node.invoke(state)
        return result
    
    return execution_node


def router(state: AgentState) -> Literal["tools", "end"]:
    """route to tools or end based on agent response."""
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "end"
