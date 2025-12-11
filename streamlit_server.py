"""streamlit ui server entry point."""

import os
import streamlit as st
from dotenv import load_dotenv
from src.channels.streamlit import LLMInterface
from src.config import DEFAULT_LLM_MODEL, DEFAULT_TEMPERATURE

load_dotenv()


def main():
    """main function to launch the interface."""
    if not os.getenv("OPENAI_API_KEY"):
        st.error("error: openai_api_key not found in environment variables")
        st.info("please set it in a .env file or export it")
        return

    llm_model = os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL)
    temperature = float(os.getenv("TEMPERATURE", str(DEFAULT_TEMPERATURE)))

    interface = LLMInterface(llm_model=llm_model, temperature=temperature)
    interface.launch()


if __name__ == "__main__":
    main()
