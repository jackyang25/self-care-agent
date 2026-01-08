"""node functions for agent graph."""

import logging
from typing import Callable, Dict, Literal

from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from src.application.agent.state import AgentState

logger = logging.getLogger(__name__)


def create_reasoning_node(llm_with_tools: ChatOpenAI) -> Callable[[AgentState], Dict]:
    """create reasoning node.

    args:
        llm_with_tools: llm with tools bound

    returns:
        reasoning node function
    """

    def reasoning_node(state: AgentState) -> Dict:
        """invoke LLM for reasoning and planning."""
        logger.info("Invoking LLM")

        system_prompt = state["system_prompt"]
        # use a real SystemMessage to avoid mixing dicts with LangChain message objects
        messages = [SystemMessage(content=system_prompt), *state["messages"]]
        response = llm_with_tools.invoke(messages)

        # log tool calls if present
        if response.tool_calls:
            tool_names = [tc.get("name", "unknown") for tc in response.tool_calls]
            logger.info(f"Planned tools {{{', '.join(tool_names)}}}")

        return {"messages": [response]}

    return reasoning_node


def create_tools_node(tool_node: ToolNode) -> Callable[[AgentState], Dict]:
    """create tools node.

    args:
        tool_node: langgraph tool node that invokes tools

    returns:
        tools node function
    """

    def tools_node(state: AgentState) -> Dict:
        """invoke tools and extract structured data from artifacts.

        uses ToolNode to invoke tools once, then extracts structured outputs
        from ToolMessage artifacts.
        """
        logger.info("Invoking tools")

        # invoke tools through ToolNode (single invocation)
        result = tool_node.invoke(state)

        # extract structured data from ToolMessage artifacts
        tool_outputs_captured = []
        sources_captured = []

        for msg in result.get("messages", []):
            # capture all tool calls
            if hasattr(msg, "name") and msg.name:
                tool_name = msg.name

                # capture tool output (with or without artifact)
                if hasattr(msg, "artifact") and msg.artifact:
                    # has structured artifact
                    output_dict = (
                        msg.artifact.model_dump()
                        if hasattr(msg.artifact, "model_dump")
                        else msg.artifact
                    )
                    tool_outputs_captured.append(
                        {"tool": tool_name, "output": output_dict}
                    )

                    # extract sources if this is the knowledge base tool
                    if tool_name == "search_knowledge_base_tool":
                        docs = output_dict.get("documents", [])
                        for doc in docs:
                            sources_captured.append(
                                {
                                    "title": doc.get("title") or "Unknown",
                                    "source": doc.get("source")
                                    or doc.get("source_name"),
                                    "content_type": doc.get("content_type"),
                                    "similarity": doc.get("similarity"),
                                }
                            )
                else:
                    # no artifact, just capture tool name
                    tool_outputs_captured.append({"tool": tool_name, "output": None})

        logger.info(
            f"Tools executed {{captured_outputs={len(tool_outputs_captured)}, captured_sources={len(sources_captured)}}}"
        )

        # return messages, tool outputs, AND sources
        return {
            "messages": result.get("messages", []),
            "tool_outputs": tool_outputs_captured,
            "sources": sources_captured,
        }

    return tools_node


def routing_node(state: AgentState) -> Literal["tools", "end"]:
    """route to tools or end based on agent response."""
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        logger.info("Routing to tools")
        return "tools"
    logger.info("Routing to end")
    return "end"
