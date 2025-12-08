"""main entry point for the llm streamlit application."""

import os
import streamlit as st
from dotenv import load_dotenv
from src.interface import LLMInterface

load_dotenv()


def main():
    """main function to launch the interface."""
    if not os.getenv("OPENAI_API_KEY"):
        st.error("error: openai_api_key not found in environment variables")
        st.info("please set it in a .env file or export it")
        return

    llm_model = os.getenv("LLM_MODEL", "gpt-4o")
    temperature = float(os.getenv("TEMPERATURE", "0.3"))

    interface = LLMInterface(llm_model=llm_model, temperature=temperature)
    interface.launch()


if __name__ == "__main__":
    main()
