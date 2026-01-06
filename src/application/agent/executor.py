"""agent executor for message processing."""

from typing import Any, Optional

from langchain_core.messages import HumanMessage

from src.application.agent.graph import create_agent_graph
from src.application.agent.prompt import SYSTEM_PROMPT
from src.application.services.interactions import (
    extract_rag_sources,
    extract_tool_info_from_messages,
    save_interaction,
)
from src.infrastructure.redis import (
    get_conversation_history,
    save_conversation_history,
)
from src.shared.config import LLM_MODEL, TEMPERATURE
from src.shared.context import UserContext
import logging

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
        logger.info(f"initialized agent | model={LLM_MODEL} | temperature={TEMPERATURE}")
    return _agent_instance


def process_message(
    agent: Any,
    user_input: str,
    user_id: Optional[str] = None,
    user_age: Optional[int] = None,
    user_gender: Optional[str] = None,
    user_timezone: Optional[str] = None,
    user_country: Optional[str] = None,
) -> tuple[str, list[dict[str, str]]]:
    """process user message through agent.

    args:
        agent: compiled langgraph agent
        user_input: user message text
        user_id: user uuid
        user_age: user age for triage/context
        user_gender: user gender for triage/context
        user_timezone: user timezone (default: UTC)
        user_country: user country context (e.g., "za", "ke")

    returns:
        tuple of (response text, rag sources)
    """
    # create user context
    user_context = UserContext(
        user_id=user_id,
        age=user_age,
        gender=user_gender,
        timezone=user_timezone or "UTC",
        country=user_country,
    )

    # build system prompt with patient context
    patient_context = user_context.build_patient_context_section()
    system_prompt = SYSTEM_PROMPT + patient_context

    # load conversation history and add current message
    messages = get_conversation_history(user_id) if user_id else []
    messages.append(HumanMessage(content=user_input))

    # log workflow start
    query_preview = user_input[:100] + "..." if len(user_input) > 100 else user_input
    user_info = f" | user={user_id[:8]}" if user_id else ""
    logger.info("=" * 80)
    logger.info(f"workflow start | query=\"{query_preview}\"{user_info}")

    # invoke agent
    state = {
        "messages": messages,
        "user_context": user_context,
        "system_prompt": system_prompt,
    }
    result = agent.invoke(state)
    result_messages = result["messages"]

    # save conversation history
    if user_id:
        save_conversation_history(user_id, result_messages)

    # extract data from results
    rag_sources = extract_rag_sources(result_messages)
    tool_data = extract_tool_info_from_messages(result_messages)

    # save interaction
    interaction_id = save_interaction(
        user_input=user_input,
        channel="streamlit",
        protocol_invoked=tool_data.get("protocol_invoked"),
        protocol_version=tool_data.get("protocol_version"),
        triage_result=tool_data.get("triage_result"),
        risk_level=tool_data.get("risk_level"),
        recommendations=tool_data.get("recommendations"),
        tools_called=tool_data.get("tools_called"),
        user_id=user_id,
    )

    # log completion
    tools = tool_data.get("tools_called")
    tools_str = f" | tools={', '.join(tools)}" if tools else ""
    id_str = f" | id={interaction_id[:8]}" if interaction_id else ""
    logger.info(f"workflow complete{tools_str}{id_str}")
    logger.info("=" * 80)

    # return response
    return result_messages[-1].content, rag_sources
