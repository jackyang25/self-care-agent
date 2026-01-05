"""langgraph agent with native tool calling."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, Dict, List, Literal, Optional, TypedDict

import pytz
import yaml
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from src.tools import TOOLS
from src.utils.context import (
    current_user_age,
    current_user_country,
    current_user_gender,
    current_user_id,
    current_user_timezone,
)
from src.services.interactions import extract_tool_info_from_messages, save_interaction
from src.utils.logger import get_logger

logger = get_logger("agent")


class AgentState(TypedDict, total=False):
    """state for the agent."""

    messages: Annotated[list, lambda x, y: x + y]
    system_prompt: Optional[str]
    user_id: Optional[str]


# configuration paths and defaults
_CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
DEFAULT_PROMPT_VERSION = "v1"


def _get_system_prompt_path() -> Path:
    """get path to system prompt yaml file."""
    return _CONFIG_DIR / "system_prompt.yaml"


def _get_agent_config_path() -> Path:
    """get path to agent config yaml file."""
    return _CONFIG_DIR / "agent_config.yaml"


def _load_agent_config() -> Dict[str, Any]:
    """load agent configuration from yaml file.

    returns:
        dict with 'llm_model' and 'temperature' keys

    raises:
        FileNotFoundError: if config file not found
        ValueError: if config file missing required fields
    """
    config_path = _get_agent_config_path()

    if not config_path.exists():
        raise FileNotFoundError(
            f"agent config file not found at {config_path}. "
            f"ensure config/agent_config.yaml exists."
        )

    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        raise ValueError(f"failed to parse yaml from {config_path}: {exc}") from exc

    llm_model = data.get("llm_model")
    temperature = data.get("temperature")

    if not llm_model:
        raise ValueError(f"missing 'llm_model' field in {config_path}")
    if temperature is None:
        raise ValueError(f"missing 'temperature' field in {config_path}")

    return {
        "llm_model": llm_model,
        "temperature": float(temperature),
    }


def _load_system_prompt() -> Dict[str, str]:
    """load system prompt from yaml file.

    supports environment variable overrides:
    - SYSTEM_PROMPT_PATH: custom path to prompt yaml file
    - SYSTEM_PROMPT_VERSION: override version metadata

    returns:
        dict with 'prompt', 'version', and 'path' keys

    raises:
        FileNotFoundError: if prompt file not found
        ValueError: if prompt file missing 'prompt' field
    """
    prompt_path_env = os.getenv("SYSTEM_PROMPT_PATH")
    prompt_path = (
        Path(prompt_path_env).expanduser()
        if prompt_path_env
        else _get_system_prompt_path()
    )

    if not prompt_path.exists():
        raise FileNotFoundError(
            f"system prompt file not found at {prompt_path}. "
            f"ensure config/system_prompt.yaml exists or set SYSTEM_PROMPT_PATH."
        )

    try:
        data = yaml.safe_load(prompt_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        raise ValueError(f"failed to parse yaml from {prompt_path}: {exc}") from exc

    prompt_text = data.get("prompt")
    if not prompt_text:
        raise ValueError(f"missing 'prompt' field in {prompt_path}")

    prompt_version = str(data.get("version", DEFAULT_PROMPT_VERSION))

    # allow env override for version metadata
    env_version = os.getenv("SYSTEM_PROMPT_VERSION")
    if env_version:
        prompt_version = env_version

    return {
        "prompt": prompt_text,
        "version": prompt_version,
        "path": str(prompt_path),
    }


# load configurations at module initialization
SYSTEM_PROMPT_DATA = _load_system_prompt()
AGENT_CONFIG = _load_agent_config()

logger.info(
    f"loaded system prompt version={SYSTEM_PROMPT_DATA['version']} from {SYSTEM_PROMPT_DATA['path']}"
)
logger.info(
    f"loaded agent config: model={AGENT_CONFIG['llm_model']}, temperature={AGENT_CONFIG['temperature']}"
)


# agent singleton
_agent_instance = None


def get_agent() -> Any:
    """get or create agent singleton.

    creates agent with configuration from config/agent_config.yaml.

    returns:
        compiled langgraph agent instance
    """
    global _agent_instance
    if _agent_instance is None:
        llm_model = AGENT_CONFIG["llm_model"]
        temperature = AGENT_CONFIG["temperature"]
        _agent_instance = create_agent(llm_model=llm_model, temperature=temperature)
        logger.info(
            f"created agent singleton: model={llm_model}, temperature={temperature}"
        )
    return _agent_instance


def create_agent(llm_model: str, temperature: float) -> Any:
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

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", call_tools)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent", should_continue, {"tools": "tools", "end": END}
    )
    workflow.add_edge("tools", "agent")

    return workflow.compile()


def _build_patient_context(
    age: Optional[int],
    gender: Optional[str],
    timezone: str,
    country: Optional[str] = None,
) -> str:
    """build patient context section for system prompt.

    args:
        age: patient age
        gender: patient gender
        timezone: patient timezone (e.g., "America/New_York")
        country: patient country context (e.g., "za", "ke", "us")

    returns:
        formatted context string to append to system prompt
    """
    context_parts = []

    # add current time in user's timezone
    try:
        tz = pytz.timezone(timezone) if timezone else pytz.UTC
        current_time = datetime.now(tz)
        time_str = current_time.strftime("%A, %B %d, %Y at %I:%M %p %Z")
    except Exception:
        current_time = datetime.now(pytz.UTC)
        time_str = current_time.strftime("%A, %B %d, %Y at %I:%M %p UTC")

    context_parts.append(f"Current time: {time_str}")

    if age is not None:
        context_parts.append(f"Age: {age}")
    if gender is not None:
        context_parts.append(f"Gender: {gender}")
    if country is not None:
        context_parts.append(f"Country: {country}")

    if not context_parts:
        return ""

    context_lines = "\n".join(f"- {part}" for part in context_parts)
    return (
        f"\n\n## current patient context\n\n{context_lines}\n\n"
        f"use this information to provide appropriate, personalized care. "
        f"use the current time to schedule appointments appropriately "
        f"(e.g., 'tomorrow' means the next day from current time). "
        f"when using rag_retrieval, country-specific clinical guidelines will be prioritized."
    )


def _extract_rag_sources(messages: List) -> List[Dict[str, Any]]:
    """extract rag sources from tool messages.

    args:
        messages: list of agent messages

    returns:
        list of source dicts with title, content_type, similarity
    """
    # find rag tool call ids
    rag_tool_call_ids = []
    for msg in messages:
        if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
            for tool_call in msg.tool_calls:
                if tool_call.get("name") == "rag_retrieval":
                    tool_call_id = tool_call.get("id")
                    if tool_call_id:
                        rag_tool_call_ids.append(tool_call_id)

    # extract sources from matching tool messages
    sources = []
    for msg in messages:
        if isinstance(msg, ToolMessage):
            tool_call_id = getattr(msg, "tool_call_id", None)
            if tool_call_id in rag_tool_call_ids:
                try:
                    data = json.loads(msg.content)
                    if isinstance(data, dict) and "documents" in data:
                        for doc in data["documents"]:
                            sources.append(
                                {
                                    "title": doc.get("title", "Unknown"),
                                    "content_type": doc.get("content_type"),
                                    "similarity": doc.get("similarity", 0),
                                }
                            )
                except (json.JSONDecodeError, KeyError, AttributeError):
                    pass

    return sources


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

    args:
        agent: compiled langgraph agent
        user_input: user message text
        conversation_history: previous messages (list of {"role": str, "content": str})
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

    patient_context = _build_patient_context(age, gender, timezone, country)
    system_prompt = SYSTEM_PROMPT_DATA["prompt"] + patient_context

    # build message history from conversation
    messages = []
    if conversation_history:
        for msg in conversation_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=user_input))

    # invoke agent with state
    state = {"messages": messages, "user_id": user_id, "system_prompt": system_prompt}
    result = agent.invoke(state)

    result_messages = result["messages"]
    last_message = result_messages[-1]

    # extract rag sources and tool data
    rag_sources = _extract_rag_sources(result_messages)
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
