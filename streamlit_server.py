"""streamlit ui server entry point."""

import os

import streamlit as st
from dotenv import load_dotenv

from src.channels.streamlit import StreamlitHandler

load_dotenv()


def main():
    """main function to launch the interface."""
    if not os.getenv("OPENAI_API_KEY"):
        st.error("error: openai_api_key not found in environment variables")
        st.info("please set it in a .env file or export it")
        return

    handler = StreamlitHandler()
    handler.launch()


if __name__ == "__main__":
    main()
