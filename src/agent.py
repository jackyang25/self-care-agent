"""langgraph agent with orchestrator for intent-based routing."""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from src.orchestrator import Orchestrator


class AgentState(TypedDict):
    """state for the agent."""

    messages: Annotated[list, lambda x, y: x + y]
    orchestrator_result: dict


def create_agent(llm_model: str = "gpt-3.5-turbo", temperature: float = 0.7):
    """create a langgraph agent with orchestrator."""
    orchestrator = Orchestrator(llm_model=llm_model, temperature=temperature)

    def process_with_orchestrator(state: AgentState):
        """process message through orchestrator."""
        user_message = state["messages"][-1].content
        result = orchestrator.process(user_message)
        return {
            "orchestrator_result": result,
            "messages": [
                AIMessage(content=f"processed: {result.get('message', 'completed')}")
            ],
        }

    workflow = StateGraph(AgentState)
    workflow.add_node("orchestrator", process_with_orchestrator)
    workflow.set_entry_point("orchestrator")
    workflow.add_edge("orchestrator", END)

    return workflow.compile()


def process_message(agent, user_input: str):
    """process a user message through the agent."""
    state = {"messages": [HumanMessage(content=user_input)], "orchestrator_result": {}}
    result = agent.invoke(state)

    # format response with orchestrator result
    tool_result = result.get("orchestrator_result", {})
    if tool_result:
        return f"intent: {tool_result.get('intent', 'unknown')}\n{tool_result.get('message', 'processed')}"
    return result["messages"][-1].content
