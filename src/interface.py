"""gradio interface for llm responses."""

import gradio as gr
from src.agent import create_agent, process_message


class LLMInterface:
    """gradio interface wrapper."""

    def __init__(self, llm_model: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """initialize the interface with agent."""
        self.agent = create_agent(llm_model=llm_model, temperature=temperature)

    def respond(self, message, history):
        """process user message and return response."""
        # build conversation history from gradio history format
        # history is list of tuples: [(user_msg, assistant_msg), ...]
        conversation_history = []
        for user_msg, assistant_msg in history:
            conversation_history.append({"role": "user", "content": user_msg})
            if assistant_msg:
                # remove tool execution info from assistant message for history
                clean_msg = assistant_msg.split("\n\n[tool execution:")[0].strip()
                conversation_history.append({"role": "assistant", "content": clean_msg})

        response = process_message(
            self.agent, message, conversation_history=conversation_history
        )
        return response

    def launch(
        self, share: bool = False, server_name: str = "0.0.0.0", server_port: int = None
    ):
        """launch the gradio interface."""
        interface = gr.ChatInterface(
            fn=self.respond,
            title="Self-Care Agent",
            description="Prototype v0",
            submit_btn="Submit",
            retry_btn="Retry",
            undo_btn="Undo",
            clear_btn="Clear",
        )
        interface.launch(share=share, server_name=server_name, server_port=server_port)
