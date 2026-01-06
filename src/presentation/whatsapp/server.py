"""webhook server entry point for channel integrations."""

import os
from dotenv import load_dotenv
import uvicorn
from src.presentation.whatsapp.handler import app
from src.infrastructure.postgres.connection import _get_connection_pool
from src.infrastructure.redis.connection import _get_redis_pool

load_dotenv()


def initialize_connections():
    """initialize database connections at startup."""
    _get_connection_pool()  # initialize postgres
    _get_redis_pool()  # initialize redis


def main():
    """run webhook server."""
    # initialize connections before starting server
    initialize_connections()
    
    port = int(os.getenv("WEBHOOK_PORT", "8000"))
    host = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()

