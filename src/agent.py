"""langgraph agent with native tool calling."""

import json
from datetime import datetime
from typing import TypedDict, Annotated, Optional, List, Dict, Any, Literal
import pytz
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from src.tools import TOOLS
from src.utils.logger import get_logger
from src.utils.context import current_user_id, current_user_age, current_user_gender, current_user_timezone
from src.utils.interactions import save_interaction, extract_tool_info_from_messages

logger = get_logger("agent")


class AgentState(TypedDict, total=False):
    """state for the agent."""

    messages: Annotated[list, lambda x, y: x + y]
    system_prompt: Optional[str]
    user_id: Optional[str]


SYSTEM_PROMPT = """you are a healthcare self-care assistant helping users access health services and commodities in low and middle income country settings.

## core workflow

**step 1: triage first**
when users report symptoms, health concerns, or ask "should i see a doctor?", immediately call triage_and_risk_flagging. this is mandatory for any health-related query.

**step 2: fulfill all requests**
after triage, review the original user request. if the user asked for medication, commodities, or services, call the appropriate tool (commodity, pharmacy, or referrals). complete all requested actions before ending.

**step 3: chain tools as needed**
use tool results to determine next steps:
- triage → commodity/pharmacy (if user requested medication)
- triage → referrals (if risk level warrants and user consents)
- analyze each tool result and call additional tools if indicated

## risk-based actions (who iitt - interagency integrated triage tool)

**red (high acuity):**
1. provide emergency safety instructions immediately (e.g., "if symptoms worsen, go to emergency immediately")
2. strongly recommend clinical evaluation
3. ask: "would you like me to schedule an appointment for you?"
4. if user agrees, ask: "do you have a preferred date and time, or would you like the earliest available?"
5. when calling referrals tool, choose appropriate specialty based on symptoms:
   - cardiac/heart/chest pain → cardiology
   - pregnancy/prenatal → obstetrics
   - children (age < 12) → pediatrics
   - otherwise → general_practice
6. only call referrals tool after explicit user consent
7. never suggest "continue monitoring" for emergency symptoms (chest pain, severe breathing difficulty, etc.)

**yellow (moderate acuity):**
1. recommend clinical evaluation soon
2. ask if user wants to schedule before calling referrals tool
3. if user agrees, ask about date/time preferences (or use earliest available if not specified)

**green (low acuity):**
1. suggest self-care or pharmacy support as appropriate
2. can wait for evaluation if needed

## safety and consent

- prioritize user safety: emergency instructions come before scheduling
- always ask for consent before scheduling appointments
- after consent, ask for scheduling preferences (date, time) before calling referrals tool
- if user doesn't specify preferences, you may use reasonable defaults
- wait for user response before proceeding with consent-required tool calls

## communication

- be clear and empathetic
- provide clear summaries when tool results indicate completion
- when confirming appointments, always include: provider name, facility, date, time, and reason
- verify you have fulfilled every part of the user's original request before ending"""


def create_agent(llm_model: str, temperature: float) -> Any:
    """create a langgraph agent with native tool calling."""
    llm = ChatOpenAI(model=llm_model, temperature=temperature)
    llm_with_tools = llm.bind_tools(TOOLS)

    tool_node = ToolNode(TOOLS)

    def should_continue(state: AgentState) -> Literal["tools", "end"]:
        """determine if we should continue or end."""
        messages = state["messages"]
        last_message = messages[-1]

        # only AIMessage can have tool_calls
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "tools"
        return "end"

    def call_model(state: AgentState) -> Dict[str, List[AIMessage]]:
        """call the llm with tools."""
        # note: user_id context is set in process_message() before agent.invoke()
        # use system prompt from state if available, otherwise use default
        system_prompt = state.get("system_prompt", SYSTEM_PROMPT)
        messages = [
            {"role": "system", "content": system_prompt},
            *state["messages"],
        ]
        response = llm_with_tools.invoke(messages)
        
        # log when agent decides to call tools
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call.get("name", "unknown")
                tool_args = tool_call.get("args", {})
                logger.info(f"calling tool: {tool_name} with args: {tool_args}")
        
        return {"messages": [response]}

    def call_tools(state: AgentState) -> Dict[str, List[ToolMessage]]:
        """call tools with user context set."""
        # note: user_id context is set in process_message() before agent.invoke()
        # call the standard tool node
        result = tool_node.invoke(state)
        
        # log tool results after execution
        if isinstance(result, dict) and "messages" in result:
            for msg in result["messages"]:
                if isinstance(msg, ToolMessage):
                    logger.info(f"tool result: {msg.content[:200]}")
        
        return result

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", call_tools)
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


def process_message(
    agent: Any,
    user_input: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    user_id: Optional[str] = None,
    user_age: Optional[int] = None,
    user_gender: Optional[str] = None,
    user_timezone: Optional[str] = None,
) -> tuple[str, list[dict[str, str]]]:
    """process a user message through the agent."""
    # set context variables once at the start for tools to access
    if user_id:
        current_user_id.set(user_id)
    if user_age is not None:
        current_user_age.set(user_age)
    if user_gender is not None:
        current_user_gender.set(user_gender)
    if user_timezone is not None:
        current_user_timezone.set(user_timezone)
    
    # build dynamic system prompt with user context
    system_prompt = SYSTEM_PROMPT
    age = current_user_age.get()
    gender = current_user_gender.get()
    timezone = current_user_timezone.get()
    
    # add patient context and current time
    context_parts = []
    
    # add current time in user's timezone
    try:
        tz = pytz.timezone(timezone) if timezone else pytz.UTC
        current_time = datetime.now(tz)
        context_parts.append(f"Current time: {current_time.strftime('%A, %B %d, %Y at %I:%M %p %Z')}")
    except Exception:
        # fallback to UTC if timezone invalid
        current_time = datetime.now(pytz.UTC)
        context_parts.append(f"Current time: {current_time.strftime('%A, %B %d, %Y at %I:%M %p UTC')}")
    
    if age is not None:
        context_parts.append(f"Age: {age}")
    if gender is not None:
        context_parts.append(f"Gender: {gender}")
    
    if context_parts:
        user_context = "\n\n## current patient context\n\n" + "\n".join(f"- {part}" for part in context_parts)
        user_context += "\n\nuse this information to provide appropriate, personalized care. use the current time to schedule appointments appropriately (e.g., 'tomorrow' means the next day from current time)."
        system_prompt = SYSTEM_PROMPT + user_context
    
    # build message history
    messages = []

    # add conversation history if provided
    if conversation_history:
        for msg in conversation_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

    # add current user message
    messages.append(HumanMessage(content=user_input))

    # pass user_id and custom system prompt in state
    state = {"messages": messages, "user_id": user_id, "system_prompt": system_prompt}
    result = agent.invoke(state)

    messages = result["messages"]
    last_message = messages[-1]

    # extract RAG sources from tool messages
    # track which tool calls were RAG to match with results
    rag_tool_call_ids = []
    for msg in messages:
        if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
            for tool_call in msg.tool_calls:
                if tool_call.get("name") == "rag_retrieval":
                    tool_call_id = tool_call.get("id")
                    if tool_call_id:
                        rag_tool_call_ids.append(tool_call_id)
    
    rag_sources = []
    for msg in messages:
        if isinstance(msg, ToolMessage):
            # check if this tool message corresponds to a RAG tool call
            tool_call_id = getattr(msg, "tool_call_id", None)
            if tool_call_id in rag_tool_call_ids:
                try:
                    # parse RAG tool response
                    data = json.loads(msg.content)
                    if isinstance(data, dict) and "documents" in data:
                        for doc in data["documents"]:
                            rag_sources.append({
                                "title": doc.get("title", "Unknown"),
                                "content_type": doc.get("content_type"),
                                "similarity": doc.get("similarity", 0),
                            })
                except (json.JSONDecodeError, KeyError, AttributeError):
                    pass

    # find tool execution info in message chain (for response formatting only)
    tool_info = []
    for i, msg in enumerate(messages):
        if isinstance(msg, ToolMessage):
            tool_info.append("tool executed")
        elif (
            isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls
        ):
            for tool_call in msg.tool_calls:
                tool_name = tool_call.get("name", "unknown")
                tool_info.append(f"tool: {tool_name}")

    # extract tool information for interaction storage
    tool_data = extract_tool_info_from_messages(messages)
    
    # save interaction to database (all interactions, not just when tools are called)
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

    if isinstance(last_message, AIMessage):
        if last_message.content:
            response = last_message.content
            if tool_info:
                response = f"{response}\n\n[tool execution: {', '.join(tool_info)}]"
            return response, rag_sources
        elif hasattr(last_message, "tool_calls") and last_message.tool_calls:
            tool_name = last_message.tool_calls[0].get("name", "unknown")
            return f"tool '{tool_name}' executed successfully", []

    return "processed", []
