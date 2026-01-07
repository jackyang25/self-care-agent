"""streamlit channel handler."""

from pathlib import Path
from typing import Optional
import uuid

import streamlit as st
from PIL import Image

import logging

from src.presentation.base import BaseChannelHandler

logger = logging.getLogger(__name__)


class StreamlitHandler(BaseChannelHandler):
    """streamlit channel handler."""

    # conversation history managed automatically by redis
    # streamlit session_state still used for UI display only
    # no need to override get_conversation_history()

    def get_user_id(self) -> Optional[str]:
        """get current user id from streamlit session state."""
        return st.session_state.get("user_id")
    
    def _render_user_config(self) -> None:
        """render user configuration interface."""
        # row 1: basic info and demographics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if "user_name" not in st.session_state:
                st.session_state.user_name = "Jack"
            name_options = ["Jack", "Sarah", "Aisha", "Thabo", "Maria", "John", "Emma", "Kwame", "Fatima", "David"]
            try:
                name_index = name_options.index(st.session_state.user_name)
            except ValueError:
                name_index = 0
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
            gender_display = {"male": "Male", "female": "Female", "other": "Other"}
            st.session_state.user_gender = st.selectbox(
                "Gender",
                options=["male", "female", "other"],
                format_func=lambda x: gender_display[x],
                index=["male", "female", "other"].index(st.session_state.user_gender),
                key="input_user_gender",
            )
        
        with col4:
            country_display = {"us": "United States", "za": "South Africa", "ke": "Kenya", "ng": "Nigeria"}
            st.session_state.country_context_id = st.selectbox(
                "Country",
                options=["us", "za", "ke", "ng"],
                format_func=lambda x: country_display[x],
                index=["us", "za", "ke", "ng"].index(st.session_state.country_context_id),
                key="input_country_context_id",
            )
        
        with col5:
            literacy_display = {"standard": "Standard", "simple": "Simple", "icons": "Icons"}
            st.session_state.literacy_mode = st.selectbox(
                "Literacy",
                options=["standard", "simple", "icons"],
                format_func=lambda x: literacy_display[x],
                index=["standard", "simple", "icons"].index(st.session_state.literacy_mode),
                key="input_literacy_mode",
            )
        
        # row 2: language, contact and channel
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            language_display = {"en": "English", "es": "Spanish", "fr": "French", "zu": "Zulu", "sw": "Swahili"}
            language_keys = list(language_display.keys())
            try:
                lang_index = language_keys.index(st.session_state.preferred_language)
            except ValueError:
                lang_index = 0
            st.session_state.preferred_language = st.selectbox(
                "Language",
                options=language_keys,
                format_func=lambda x: language_display[x],
                index=lang_index,
                key="input_preferred_language",
            )
        
        with col2:
            email_options = [
                "demo@example.com",
                "jack@example.com",
                "sarah@example.com",
                "aisha@example.com",
                "test@example.com"
            ]
            try:
                email_index = email_options.index(st.session_state.email)
            except ValueError:
                email_index = 0
            st.session_state.email = st.selectbox(
                "Email",
                options=email_options,
                index=email_index,
                key="input_email",
            )
        
        with col3:
            phone_options = [
                "+12065551234",
                "+12065552345",
                "+27115551234",
                "+254701234567",
                "+2348051234567"
            ]
            try:
                phone_index = phone_options.index(st.session_state.phone_e164)
            except ValueError:
                phone_index = 0
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
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        with col2:
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
    
    def _render_chat_interface(self) -> None:
        """render chat interface."""
        # initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # display chat history
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
                                similarity_pct = int(source.get("similarity", 0) * 100)
                                content_type = source.get("content_type", "")
                                content_type_badge = (
                                    f"`{content_type}`" if content_type else ""
                                )

                                st.markdown(
                                    f"**{i}. {source.get('title', 'Unknown')}**  "
                                    f"{content_type_badge}  "
                                    f"*({similarity_pct}% match)*"
                                )
    
    def _handle_chat_input(self, prompt: str) -> None:
        """handle user chat input and generate response."""
        # add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # get assistant response
        with st.spinner("Thinking..."):
            # pass demo user config directly (stateless)
            response, sources, tools = self.respond(
                prompt,
                user_id=st.session_state.get("user_id"),
                user_age=st.session_state.get("user_age"),
                user_gender=st.session_state.get("user_gender"),
                user_timezone=st.session_state.get("timezone", "UTC"),
                user_country=st.session_state.get("country_context_id"),
            )
            
            # store response with metadata
            response_data = {
                "role": "assistant",
                "content": response,
                "tools": tools,
                "sources": sources
            }
            st.session_state.messages.append(response_data)
        
        st.rerun()
    
    def _initialize_demo_user(self) -> None:
        """initialize demo user with default values matching database schema."""
        if "user_id" not in st.session_state:
            st.session_state.user_id = str(uuid.uuid4())
        if "fhir_patient_id" not in st.session_state:
            st.session_state.fhir_patient_id = "patient-demo-jack"
        if "primary_channel" not in st.session_state:
            st.session_state.primary_channel = "streamlit"
        if "phone_e164" not in st.session_state:
            st.session_state.phone_e164 = "+12065551234"
        if "email" not in st.session_state:
            st.session_state.email = "demo@example.com"
        if "preferred_language" not in st.session_state:
            st.session_state.preferred_language = "en"
        if "literacy_mode" not in st.session_state:
            st.session_state.literacy_mode = "standard"
        if "country_context_id" not in st.session_state:
            st.session_state.country_context_id = "us"
        if "timezone" not in st.session_state:
            st.session_state.timezone = "America/New_York"
        # demographics
        if "user_age" not in st.session_state:
            st.session_state.user_age = 24
        if "user_gender" not in st.session_state:
            st.session_state.user_gender = "male"
        # accessibility
        if "hearing_aid" not in st.session_state:
            st.session_state.hearing_aid = False
        if "visual_aid" not in st.session_state:
            st.session_state.visual_aid = False

    def launch(self) -> None:
        """launch the streamlit interface."""
        # load gates foundation logo
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


        # initialize demo user
        self._initialize_demo_user()

        # main interface
        st.title("AI Self-Care Agent Demo")
        
        # configuration in collapsible expander
        with st.expander("Configure Demo User", expanded=False):
            self._render_user_config()
        
        # chat interface
        self._render_chat_interface()
        
        # chat input (at root level for fixed bottom position)
        if prompt := st.chat_input("Type your message here..."):
            self._handle_chat_input(prompt)
