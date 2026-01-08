"""shared configuration for the application."""

import os

# llm configuration
LLM_MODEL = os.getenv("AGENT_MODEL", "gpt-4o")
TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.0"))

# embeddings configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# rag configuration
RAG_LIMIT_DEFAULT = int(os.getenv("RAG_LIMIT_DEFAULT", "5"))
RAG_MIN_SIMILARITY = float(os.getenv("RAG_MIN_SIMILARITY", "0.35"))

# API keys (do not hardcode secrets; keep them in env)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# postgres configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "selfcare")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

# webhook configuration
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8000"))

# whatsapp configuration (do not hardcode secrets; keep them in env)
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
