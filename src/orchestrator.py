"""orchestrator for intent classification and tool routing."""

import json
from typing import Dict, Any, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.tools import TOOLS


INTENTS = [
    "triage_and_risk_flagging",
    "commodity_orders_and_fulfillment",
    "pharmacy_orders_and_fulfillment",
    "referrals_and_scheduling",
]


class Orchestrator:
    """orchestrator that classifies intent and routes to tools."""

    def __init__(self, llm_model: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """initialize orchestrator with llm."""
        self.llm = ChatOpenAI(model=llm_model, temperature=temperature)
        self.tools = TOOLS

    def classify_intent(self, user_message: str) -> str:
        """classify user message into one of four intents."""
        system_prompt = f"""you are an intent classifier for a healthcare system.
analyze the user message and classify it into exactly one of these four intents:
{', '.join(INTENTS)}

return only the intent name, nothing else."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]

        response = self.llm.invoke(messages)
        intent = response.content.strip().lower()

        # validate intent
        if intent not in INTENTS:
            # try to find closest match
            for valid_intent in INTENTS:
                if valid_intent in intent or intent in valid_intent:
                    intent = valid_intent
                    break
            else:
                # default to triage if unclear
                intent = "triage_and_risk_flagging"

        return intent

    def extract_arguments(self, user_message: str, intent: str) -> Dict[str, Any]:
        """extract structured arguments from user message for the given intent."""
        system_prompt = f"""extract relevant information from the user message for the intent: {intent}.
return a json object with the extracted information. only include information that is explicitly mentioned or can be reasonably inferred.
return only valid json, no other text."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]

        response = self.llm.invoke(messages)
        
        try:
            # try to parse json from response
            content = response.content.strip()
            # remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()
            return json.loads(content)
        except json.JSONDecodeError:
            # if parsing fails, return empty dict
            return {}

    def process(self, user_message: str) -> Dict[str, Any]:
        """process user message: classify intent, extract args, call tool."""
        print(f"[ORCHESTRATOR] processing message: {user_message[:100]}...")
        
        # classify intent
        intent = self.classify_intent(user_message)
        print(f"[ORCHESTRATOR] classified intent: {intent}")
        
        # extract arguments
        arguments = self.extract_arguments(user_message, intent)
        
        # call appropriate tool
        tool = self.tools[intent]
        result = tool(**arguments)
        
        return result

