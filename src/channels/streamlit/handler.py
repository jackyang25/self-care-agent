"""streamlit channel handler - core logic only."""

import logging

import streamlit as st

from src.channels.base import BaseChannelHandler

logger = logging.getLogger(__name__)


class StreamlitHandler(BaseChannelHandler):
    """streamlit channel handler for agent communication."""

    def handle_chat_input(self, prompt: str) -> None:
        """handle user chat input and generate response.
        
        args:
            prompt: user message text
        """
        # check if we're already processing to avoid double-processing
        if st.session_state.get("processing", False):
            return
        
        # add user message and display it immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.processing = True
        st.rerun()

    def handle_agent_response(self) -> None:
        """generate agent response (called after user message is displayed)."""
        # get the last user message
        last_message = st.session_state.messages[-1]
        if last_message["role"] != "user":
            return
        
        prompt = last_message["content"]

        try:
            # prepare refill date as string if present
            refill_date = st.session_state.get("refill_due_date")
            refill_date_str = refill_date.isoformat() if refill_date else None

            # get conversation history (exclude the current message we're responding to)
            history = (
                st.session_state.messages[:-1]
                if len(st.session_state.messages) > 1
                else None
            )

            response, sources, tools = self.respond(
                user_message=prompt,
                conversation_history=history,
                # socio-technical context
                whatsapp_id=st.session_state.get("whatsapp_id"),
                patient_id=st.session_state.get("emr_patient_id"),
                literacy_level=st.session_state.get("literacy_level"),
                primary_language=st.session_state.get("primary_language"),
                network_type=st.session_state.get("network_type"),
                geospatial_tag=st.session_state.get("geospatial_tag"),
                social_context=st.session_state.get("social_context"),
                # patient summary (IPS)
                patient_age=st.session_state.get("patient_age"),
                patient_gender=st.session_state.get("patient_gender"),
                active_diagnoses=st.session_state.get("active_diagnoses"),
                current_medications=st.session_state.get("current_medications"),
                allergies=st.session_state.get("allergies"),
                latest_vitals=st.session_state.get("latest_vitals"),
                adherence_score=st.session_state.get("adherence_score"),
                refill_due_date=refill_date_str,
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response,
                    "tools": tools,
                    "sources": sources,
                }
            )

        except Exception as e:
            logger.exception("agent response failed")
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": f"Sorry — I ran into an error while responding: {str(e)}",
                    "tools": [],
                    "sources": [],
                }
            )

        st.session_state.processing = False
        st.rerun()
