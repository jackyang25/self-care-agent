"""agent executor for message processing."""

from typing import Any, Optional, List, Dict
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

import logging

from src.application.agent.graph import create_agent_graph
from src.application.agent.prompt import build_system_prompt_with_context
from src.shared.config import LLM_MODEL, TEMPERATURE
from src.shared.schemas.context import RequestContext

logger = logging.getLogger(__name__)

# agent singleton
_agent_instance = None


def get_agent() -> Any:
    """get or create agent singleton.

    returns:
        compiled langgraph agent instance
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = create_agent_graph(
            llm_model=LLM_MODEL, temperature=TEMPERATURE
        )
    return _agent_instance


def convert_message_dict_to_langchain(msg: Dict[str, str]) -> BaseMessage:
    """convert message dict to LangChain message object.

    args:
        msg: dict with 'role' and 'content' keys

    returns:
        LangChain message object
    """
    role = msg.get("role", "user")
    content = msg.get("content", "")

    if role == "user":
        return HumanMessage(content=content)
    elif role == "assistant":
        return AIMessage(content=content)
    else:
        # default to human message
        return HumanMessage(content=content)


def process_message(
    agent: Any,
    user_message: str,
    context: Optional[RequestContext] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> tuple[str, list[dict[str, str]], list[str]]:
    """process user message through agent with optional conversation history.

    args:
        agent: compiled langgraph agent
        user_message: current user message
        context: request context (socio-technical + IPS fields for agent reasoning)
        conversation_history: previous conversation messages from frontend (optional)
                             format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

    returns:
        tuple of (response text, rag sources, tools called)
    """
    # use default context if none provided
    if context is None:
        context = RequestContext()

    # enrich system prompt with patient context
    system_prompt = build_system_prompt_with_context(context)

    # convert previous messages from frontend (if provided)
    langchain_messages = []
    if conversation_history:
        for msg in conversation_history:
            langchain_messages.append(convert_message_dict_to_langchain(msg))

    # add current user message
    langchain_messages.append(HumanMessage(content=user_message))

    # log workflow start
    message_preview = (
        user_message[:100] + "..." if len(user_message) > 100 else user_message
    )
    history_info = (
        f", history={len(conversation_history)} msgs" if conversation_history else ""
    )
    logger.info("=" * 80)
    logger.info(f'Workflow started {{message="{message_preview}"{history_info}}}')

    # invoke agent
    state = {
        "messages": langchain_messages,
        "config_context": context.model_dump(),
        "system_prompt": system_prompt,
        "tool_outputs": [],  # initialize empty
        "sources": [],  # initialize empty
    }
    result = agent.invoke(state)

    # read data directly from state (populated DURING tool execution - clean!)
    rag_sources = result.get("sources", [])
    tools_called = [output.get("tool") for output in result.get("tool_outputs", [])]

    # log completion
    tools_str = f" {{tools=[{', '.join(tools_called)}]}}" if tools_called else ""
    logger.info(f"Workflow completed{tools_str}")
    logger.info("=" * 80)

    # return response with sources and tools
    return result["messages"][-1].content, rag_sources, tools_called
