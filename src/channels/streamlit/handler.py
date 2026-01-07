"""streamlit channel handler."""

import logging
import uuid
from pathlib import Path
from typing import Optional

import streamlit as st
from PIL import Image

from src.channels.base import BaseChannelHandler

logger = logging.getLogger(__name__)


class StreamlitHandler(BaseChannelHandler):
    """streamlit channel handler."""

    def get_session_id(self) -> Optional[str]:
        """get current session id from streamlit session state."""
        return st.session_state.get("session_id")

    def _render_user_config(self) -> None:
        """render user configuration interface."""
        # basic info and demographics
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            name_options = ["Jack", "Sarah", "Aisha", "Thabo", "Maria", "John", "Emma", "Kwame", "Fatima", "David"]
            name_index = name_options.index(st.session_state.user_name) if st.session_state.user_name in name_options else 0
            st.session_state.user_name = st.selectbox(
                "Name",
                options=name_options,
                index=name_index,
                key="input_user_name",
            )

        with col2:
            st.session_state.user_age = st.selectbox(
                "Age",
                options=list(range(1, 121)),
                index=st.session_state.user_age - 1,
                key="input_user_age",
            )

        with col3:
            gender_options = ["male", "female", "other"]
            gender_display = {"male": "Male", "female": "Female", "other": "Other"}
            st.session_state.user_gender = st.selectbox(
                "Gender",
                options=gender_options,
                format_func=lambda x: gender_display[x],
                index=gender_options.index(st.session_state.user_gender),
                key="input_user_gender",
            )

        with col4:
            country_options = ["us", "za", "ke", "ng"]
            country_display = {"us": "United States", "za": "South Africa", "ke": "Kenya", "ng": "Nigeria"}
            st.session_state.country_context_id = st.selectbox(
                "Country",
                options=country_options,
                format_func=lambda x: country_display[x],
                index=country_options.index(st.session_state.country_context_id),
                key="input_country_context_id",
            )

        with col5:
            literacy_options = ["standard", "simple", "icons"]
            literacy_display = {"standard": "Standard", "simple": "Simple", "icons": "Icons"}
            st.session_state.literacy_mode = st.selectbox(
                "Literacy",
                options=literacy_options,
                format_func=lambda x: literacy_display[x],
                index=literacy_options.index(st.session_state.literacy_mode),
                key="input_literacy_mode",
            )

        # language, contact and accessibility
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            language_options = ["en", "es", "fr", "zu", "sw"]
            language_display = {"en": "English", "es": "Spanish", "fr": "French", "zu": "Zulu", "sw": "Swahili"}
            lang_index = language_options.index(st.session_state.preferred_language) if st.session_state.preferred_language in language_options else 0
            st.session_state.preferred_language = st.selectbox(
                "Language",
                options=language_options,
                format_func=lambda x: language_display[x],
                index=lang_index,
                key="input_preferred_language",
            )

        with col2:
            email_options = ["demo@example.com", "jack@example.com", "sarah@example.com", "aisha@example.com", "test@example.com"]
            email_index = email_options.index(st.session_state.email) if st.session_state.email in email_options else 0
            st.session_state.email = st.selectbox(
                "Email",
                options=email_options,
                index=email_index,
                key="input_email",
            )

        with col3:
            phone_options = ["+12065551234", "+12065552345", "+27115551234", "+254701234567", "+2348051234567"]
            phone_index = phone_options.index(st.session_state.phone_e164) if st.session_state.phone_e164 in phone_options else 0
            st.session_state.phone_e164 = st.selectbox(
                "Phone",
                options=phone_options,
                index=phone_index,
                key="input_phone_e164",
            )

        with col4:
            st.session_state.hearing_aid = st.checkbox(
                "Hearing Aid",
                value=st.session_state.hearing_aid,
                key="input_hearing_aid",
            )

        with col5:
            st.session_state.visual_aid = st.checkbox(
                "Visual Aid",
                value=st.session_state.visual_aid,
                key="input_visual_aid",
            )

        # action buttons
        st.markdown("---")
        st.markdown(f"**User ID:** `{st.session_state.user_id}`")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Reset User", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        with col2:
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

    def _render_chat_interface(self) -> None:
        """render chat interface."""
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

                # display tools and sources for assistant messages
                if message["role"] == "assistant":
                    tools = message.get("tools")
                    sources = message.get("sources")

                    if tools:
                        st.caption(f"Tools: {', '.join(tools)}")

                    if sources:
                        with st.expander("Sources", expanded=False):
                            for i, source in enumerate(sources, 1):
                                similarity = int(source.get("similarity", 0) * 100)
                                content_type = source.get("content_type", "")
                                type_badge = f"`{content_type}`" if content_type else ""
                                title = source.get("title", "Unknown")

                                st.markdown(
                                    f"**{i}. {title}** {type_badge} *({similarity}% match)*"
                                )

    def _handle_chat_input(self, prompt: str) -> None:
        """handle user chat input and generate response."""
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Thinking..."):
            response, sources, tools = self.respond(
                prompt,
                user_id=st.session_state.get("user_id"),
                user_age=st.session_state.get("user_age"),
                user_gender=st.session_state.get("user_gender"),
                user_timezone=st.session_state.get("timezone", "UTC"),
                user_country=st.session_state.get("country_context_id"),
            )

            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "tools": tools,
                "sources": sources
            })

        st.rerun()

    def _initialize_demo_user(self) -> None:
        """initialize demo user with default values."""
        defaults = {
            "user_id": str(uuid.uuid4()),
            "user_name": "Jack",
            "fhir_patient_id": "patient-demo-jack",
            "primary_channel": "streamlit",
            "phone_e164": "+12065551234",
            "email": "demo@example.com",
            "preferred_language": "en",
            "literacy_mode": "standard",
            "country_context_id": "us",
            "timezone": "America/New_York",
            "user_age": 24,
            "user_gender": "male",
            "hearing_aid": False,
            "visual_aid": False,
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def launch(self) -> None:
        """launch the streamlit interface."""
        # load logo if available
        logo_path = Path("src/assets/gates_logo.png")
        page_icon = None
        if logo_path.exists():
            try:
                page_icon = Image.open(str(logo_path))
            except Exception:
                pass

        st.set_page_config(
            page_title="AI Self-Care Agent Demo",
            page_icon=page_icon,
            layout="centered",
        )

        self._initialize_demo_user()

        st.title("AI Self-Care Agent Demo")

        with st.expander("Configure Demo User", expanded=False):
            self._render_user_config()

        self._render_chat_interface()

        if prompt := st.chat_input("Type your message here..."):
            self._handle_chat_input(prompt)
