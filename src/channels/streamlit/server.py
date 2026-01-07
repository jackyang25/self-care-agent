"""streamlit ui server entry point."""

import os

import streamlit as st
from dotenv import load_dotenv

from src.channels.streamlit.handler import StreamlitHandler
from src.channels.streamlit.ui import launch_app
from src.infrastructure.postgres.connection import _get_connection_pool

load_dotenv()


def initialize_connections():
    """initialize database connections at startup."""
    _get_connection_pool()  # initialize postgres


def main():
    """main function to launch the interface."""
    if not os.getenv("OPENAI_API_KEY"):
        st.error("error: openai_api_key not found in environment variables")
        st.info("please set it in a .env file or export it")
        return
    
    # initialize connections before handling any requests
    initialize_connections()

    handler = StreamlitHandler()
    launch_app(handler)


if __name__ == "__main__":
    main()
