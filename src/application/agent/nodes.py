"""node functions for agent graph."""

import logging
from typing import Callable, Dict, List, Literal

from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from src.application.agent.state import AgentState

logger = logging.getLogger(__name__)


def create_reasoning_node(llm_with_tools: ChatOpenAI) -> Callable[[AgentState], Dict[str, List[AIMessage]]]:
    """create reasoning node.
    
    args:
        llm_with_tools: llm with tools bound
        
    returns:
        reasoning node function
    """
    def reasoning_node(state: AgentState) -> Dict[str, List[AIMessage]]:
        """invoke LLM for reasoning and planning."""
        logger.info("Invoking LLM")

        system_prompt = state["system_prompt"]
        messages = [{"role": "system", "content": system_prompt}, *state["messages"]]
        response = llm_with_tools.invoke(messages)
        
        # log tool calls if present
        if response.tool_calls:
            tool_names = [tc.get("name", "unknown") for tc in response.tool_calls]
            logger.info(f"Planned tools {{{', '.join(tool_names)}}}")

        return {"messages": [response]}
    
    return reasoning_node


def create_tools_node(tool_node: ToolNode) -> Callable[[AgentState], Dict[str, List[ToolMessage]]]:
    """create tools node.
    
    args:
        tool_node: langgraph tool node that invokes tools
        
    returns:
        tools node function
    """
    def tools_node(state: AgentState) -> Dict[str, List[ToolMessage]]:
        """invoke tools with agent-provided arguments.
        
        agent has full context via system prompt and decides what to pass to tools.
        no implicit injection - agent makes explicit, informed decisions.
        """
        logger.info("Invoking tools")
        
        result = tool_node.invoke(state)
        logger.info("Completed")
        return result
    
    return tools_node


def routing_node(state: AgentState) -> Literal["tools", "end"]:
    """route to tools or end based on agent response."""
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        logger.info("Routing to tools")
        return "tools"
    logger.info("Routing to end")
    return "end"
