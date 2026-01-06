"""shared configuration for the application."""

import os

# llm configuration
LLM_MODEL = os.getenv("AGENT_MODEL", "gpt-4o")
TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.0"))
