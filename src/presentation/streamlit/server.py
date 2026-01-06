"""streamlit ui server entry point."""

import os

import streamlit as st
from dotenv import load_dotenv

from src.presentation.streamlit.handler import StreamlitHandler
from src.infrastructure.postgres.connection import _get_connection_pool
from src.infrastructure.redis.connection import _get_redis_pool

load_dotenv()


def initialize_connections():
    """initialize database connections at startup."""
    _get_connection_pool()  # initialize postgres
    _get_redis_pool()  # initialize redis


def main():
    """main function to launch the interface."""
    if not os.getenv("OPENAI_API_KEY"):
        st.error("error: openai_api_key not found in environment variables")
        st.info("please set it in a .env file or export it")
        return
    
    # initialize connections before handling any requests
    initialize_connections()

    handler = StreamlitHandler()
    handler.launch()


if __name__ == "__main__":
    main()
