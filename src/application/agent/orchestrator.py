"""agent orchestration and message processing."""

from typing import Any, Dict, List, Optional

from langchain_core.messages import AIMessage, HumanMessage

from src.application.agent.config import AGENT_CONFIG, PROMPT_DATA, build_patient_context
from src.application.agent.graph import create_agent_graph
from src.application.agent.utils import extract_rag_sources
from src.application.services.interactions import (
    extract_tool_info_from_messages,
    save_interaction,
)
from src.infrastructure.redis import (
    get_conversation_history,
    save_conversation_history,
)
from src.shared.context import (
    current_user_age,
    current_user_country,
    current_user_gender,
    current_user_id,
    current_user_timezone,
)
from src.shared.logger import get_logger

logger = get_logger("agent.orchestrator")

# agent singleton
_agent_instance = None


def get_agent() -> Any:
    """get or create agent singleton.

    conversation history is managed separately via custom redis manager
    for full control over PHI data storage and compliance.

    returns:
        compiled langgraph agent instance
    """
    global _agent_instance
    if _agent_instance is None:
        llm_model = AGENT_CONFIG["llm_model"]
        temperature = AGENT_CONFIG["temperature"]
        
        _agent_instance = create_agent_graph(llm_model=llm_model, temperature=temperature)
        logger.info(
            f"created agent singleton: model={llm_model}, temperature={temperature}"
        )
    return _agent_instance


def process_message(
    agent: Any,
    user_input: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    user_id: Optional[str] = None,
    user_age: Optional[int] = None,
    user_gender: Optional[str] = None,
    user_timezone: Optional[str] = None,
    user_country: Optional[str] = None,
) -> tuple[str, list[dict[str, str]]]:
    """process user message through agent and return response with sources.

    conversation history is automatically loaded from redis for the user_id
    and updated after processing.

    args:
        agent: compiled langgraph agent
        user_input: user message text
        conversation_history: optional override for history (uses redis if not provided)
        user_id: user uuid
        user_age: user age for triage/context
        user_gender: user gender for triage/context
        user_timezone: user timezone for scheduling (default: UTC)
        user_country: user country context for RAG filtering (e.g., "za", "ke")

    returns:
        tuple of (response text, rag sources)
    """
    # set context variables for tools to access
    if user_id:
        current_user_id.set(user_id)
    if user_age is not None:
        current_user_age.set(user_age)
    if user_gender is not None:
        current_user_gender.set(user_gender)
    if user_timezone is not None:
        current_user_timezone.set(user_timezone)
    if user_country is not None:
        current_user_country.set(user_country)

    # build system prompt with patient context
    age = current_user_age.get()
    gender = current_user_gender.get()
    timezone = current_user_timezone.get() or "UTC"
    country = current_user_country.get()

    patient_context = build_patient_context(age, gender, timezone, country)
    system_prompt = PROMPT_DATA["prompt"] + patient_context

    # load conversation history from redis (if not provided)
    if conversation_history is None and user_id:
        messages = get_conversation_history(user_id)
        logger.debug(f"loaded {len(messages)} messages from redis for user {user_id[:8]}...")
    else:
        # convert dict history to message objects
        messages = []
        if conversation_history:
            for msg in conversation_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))

    # add current user message
    user_message = HumanMessage(content=user_input)
    messages.append(user_message)

    # invoke agent with state
    state = {"messages": messages, "user_id": user_id, "system_prompt": system_prompt}
    result = agent.invoke(state)

    result_messages = result["messages"]
    last_message = result_messages[-1]

    # save updated conversation history to redis
    if user_id:
        save_conversation_history(user_id, result_messages)

    # extract rag sources and tool data
    rag_sources = extract_rag_sources(result_messages)
    tool_data = extract_tool_info_from_messages(result_messages)

    # save interaction to database
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

    if interaction_id:
        logger.info(f"saved interaction: {interaction_id}")

    # format response
    if isinstance(last_message, AIMessage):
        if last_message.content:
            # append tool execution summary for debugging
            tool_names = [
                tool_call.get("name", "unknown")
                for msg in result_messages
                if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls")
                for tool_call in (msg.tool_calls or [])
            ]
            response = last_message.content
            if tool_names:
                response += f"\n\n[tools used: {', '.join(set(tool_names))}]"
            return response, rag_sources
        elif hasattr(last_message, "tool_calls") and last_message.tool_calls:
            tool_name = last_message.tool_calls[0].get("name", "unknown")
            return f"tool '{tool_name}' executed successfully", []

    return "processed", []
