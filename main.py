"""main entry point for the llm gradio application."""

import os
from dotenv import load_dotenv
from src.interface import LLMInterface

load_dotenv()


def main():
    """main function to launch the interface."""
    if not os.getenv("OPENAI_API_KEY"):
        print("error: openai_api_key not found in environment variables")
        print("please set it in a .env file or export it")
        return

    llm_model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    temperature = float(os.getenv("TEMPERATURE", "0.7"))
    server_port = (
        int(os.getenv("GRADIO_SERVER_PORT", "0"))
        if os.getenv("GRADIO_SERVER_PORT")
        else None
    )

    interface = LLMInterface(llm_model=llm_model, temperature=temperature)
    interface.launch(server_port=server_port)


if __name__ == "__main__":
    main()
