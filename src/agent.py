"""langgraph agent with native tool calling."""

from typing import TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from src.tools import TOOLS
from src.utils.logger import get_logger
from src.utils.context import current_user_id

logger = get_logger("agent")


class AgentState(TypedDict, total=False):
    """state for the agent."""

    messages: Annotated[list, lambda x, y: x + y]
    system_prompt: Optional[str]
    user_id: Optional[str]


SYSTEM_PROMPT = """you are a healthcare self-care assistant helping users access health services and commodities in low and middle income country settings.

your role:
- assess user needs through triage and risk evaluation
- guide users to appropriate care pathways (self-care, pharmacy, telemedicine, or clinical care)
- facilitate access to health commodities and services
- coordinate referrals and appointments when needed

tool usage guidelines:
1. always start with triage when users report symptoms or health concerns
2. fulfill all parts of user requests - if user asks for both assessment AND medication/commodity/service, you MUST address both before ending
3. after calling triage, review the original user request - if user asked for medication, commodities, or services, you MUST call the appropriate tool to fulfill that request
4. do not end your response until all explicitly requested actions are completed - if user says "I have X and need Y", complete both X (triage) and Y (commodity/pharmacy/referral)
5. analyze tool results carefully - if a tool indicates another action is needed, call the appropriate tool
6. chain tools when necessary: triage may lead to commodity orders, pharmacy refills, or referrals
7. use tools sequentially to complete multi-step workflows (e.g., triage → commodity order, triage → referral → scheduling)
8. if user explicitly requests medication, commodities, or services, call the appropriate tool even after triage - do not skip this step
9. if a tool result is insufficient or indicates escalation, call additional tools as needed
10. for high-risk or critical cases: strongly recommend clinical evaluation, provide emergency instructions if needed (e.g., "if symptoms worsen, go to emergency immediately"), and explicitly ask "would you like me to schedule an appointment for you?" before calling the referrals tool - do not auto-schedule without explicit user consent
11. for medium-risk cases: ask the user if they would like to schedule an appointment before calling the referrals tool
12. prioritize emergency instructions over scheduling when symptoms are life-threatening - provide immediate safety guidance first, then ask about scheduling
13. do not accept "continue monitoring" for high-risk symptoms like chest pain, severe difficulty breathing, or other emergency symptoms

important:
- always ask for consent before scheduling appointments, even for high-risk cases
- prioritize user safety - provide emergency instructions immediately when needed
- be clear and empathetic in your responses
- if you need user consent or more information, respond with a question instead of calling tools
- wait for user response before proceeding with tool calls that require consent
- ensure each tool call serves a specific purpose in helping the user
- complete all requested actions before providing final response - check the original user request after each tool call to ensure nothing was missed
- when tool results indicate completion, provide a clear summary to the user
- before ending, verify you have fulfilled every part of the user's original request"""


def create_agent(llm_model: str, temperature: float):
    """create a langgraph agent with native tool calling."""
    llm = ChatOpenAI(model=llm_model, temperature=temperature)
    llm_with_tools = llm.bind_tools(TOOLS)

    tool_node = ToolNode(TOOLS)

    def should_continue(state: AgentState):
        """determine if we should continue or end."""
        messages = state["messages"]
        last_message = messages[-1]

        # only AIMessage can have tool_calls
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "tools"
        return "end"

    def call_model(state: AgentState):
        """call the llm with tools."""
        # set user_id in context for tools to access
        user_id = state.get("user_id")
        if user_id:
            current_user_id.set(user_id)
        
        # use system prompt from state if available, otherwise use default
        system_prompt = state.get("system_prompt", SYSTEM_PROMPT)
        messages = [
            {"role": "system", "content": system_prompt},
            *state["messages"],
        ]
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


def process_message(agent, user_input: str, conversation_history=None, user_id=None):
    """process a user message through the agent."""
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

    # pass user_id in state (tools can access via context var)
    state = {"messages": messages, "user_id": user_id}
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
