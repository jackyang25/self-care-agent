"""streamlit interface for llm responses."""

import streamlit as st
from pathlib import Path
from PIL import Image
from src.agent import create_agent, process_message


class LLMInterface:
    """streamlit interface wrapper."""

    def __init__(self, llm_model: str, temperature: float):
        """initialize the interface with agent."""
        if "agent" not in st.session_state:
            st.session_state.agent = create_agent(llm_model=llm_model, temperature=temperature)
        self.agent = st.session_state.agent

    def respond(self, message):
        """process user message and return response."""
        # build conversation history from streamlit session state
        conversation_history = []
        if "messages" in st.session_state:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    conversation_history.append({"role": "user", "content": msg["content"]})
                elif msg["role"] == "assistant":
                    # remove tool execution info from assistant message for history
                    clean_msg = msg["content"].split("\n\n[tool execution:")[0].strip()
                    conversation_history.append({"role": "assistant", "content": clean_msg})

        response = process_message(
            self.agent, message, conversation_history=conversation_history
        )
        return response

    def launch(self):
        """launch the streamlit interface."""
        # load gates foundation logo
        logo_path = Path("assets/gates_logo.png")
        page_icon = None
        if logo_path.exists():
            try:
                page_icon = Image.open(str(logo_path))
            except Exception:
                pass
        
        st.set_page_config(
            page_title="Self-Care Agent",
            page_icon=page_icon,
            layout="centered",
        )

        st.title("Self-Care Agent")
        st.caption("Prototype v0")

        # initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # chat input
        if prompt := st.chat_input("Type your message here..."):
            # add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # get assistant response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = self.respond(prompt)
                    st.markdown(response)
                    # add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})

        # clear button
        if st.sidebar.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()
