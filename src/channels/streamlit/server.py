"""streamlit ui server entry point."""

import streamlit as st
from dotenv import load_dotenv

from src.channels.streamlit.handler import StreamlitHandler
from src.channels.streamlit.ui import launch_app
from src.infrastructure.postgres.connection import _get_connection_pool
from src.shared.config import OPENAI_API_KEY
from src.shared.logger import setup_logging

load_dotenv()


def initialize_connections():
    """initialize database connections at startup."""
    _get_connection_pool()  # initialize postgres


def main():
    """main function to launch the interface."""
    # configure logging first
    setup_logging()

    if not OPENAI_API_KEY:
        st.error("error: openai_api_key not found in environment variables")
        st.info("please set it in a .env file or export it")
        return

    # initialize connections before handling any requests
    initialize_connections()

    handler = StreamlitHandler()
    launch_app(handler)


if __name__ == "__main__":
    main()
