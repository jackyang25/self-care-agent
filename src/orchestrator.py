"""orchestrator using native function calling with langchain tools."""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from src.tools import TOOLS


class Orchestrator:
    """orchestrator using native function calling."""

    def __init__(self, llm_model: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """initialize orchestrator with llm and tools."""
        self.llm = ChatOpenAI(model=llm_model, temperature=temperature).bind_tools(TOOLS)
        self.tools = {tool.name: tool for tool in TOOLS}

    def process(self, user_message: str) -> Dict[str, Any]:
        """process user message using native function calling."""
        print(f"[ORCHESTRATOR] processing message: {user_message[:100]}...")

        messages = [HumanMessage(content=user_message)]
        response = self.llm.invoke(messages)

        if response.tool_calls:
            tool_call = response.tool_calls[0]
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            print(f"[ORCHESTRATOR] tool selected: {tool_name}")
            print(f"[ORCHESTRATOR] tool arguments: {tool_args}")

            tool = self.tools[tool_name]
            result = tool.invoke(tool_args)

            return {
                "intent": tool_name,
                "message": result,
                "status": "success",
            }
        else:
            return {
                "intent": "none",
                "message": response.content,
                "status": "no_tool_called",
            }
