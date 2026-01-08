"""webhook server entry point for channel integrations."""

from dotenv import load_dotenv
import uvicorn

from src.channels.whatsapp.handler import app
from src.infrastructure.postgres.connection import _get_connection_pool
from src.shared.config import WEBHOOK_HOST, WEBHOOK_PORT
from src.shared.logger import setup_logging

load_dotenv()


def initialize_connections():
    """initialize database connections at startup."""
    _get_connection_pool()  # initialize postgres


def main():
    """run webhook server."""
    # configure logging first
    setup_logging()

    # initialize connections before starting server
    initialize_connections()

    uvicorn.run(app, host=WEBHOOK_HOST, port=WEBHOOK_PORT, log_level="info")


if __name__ == "__main__":
    main()
