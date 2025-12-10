"""streamlit interface for llm responses."""

import streamlit as st
from pathlib import Path
from PIL import Image
from src.agent import create_agent, process_message
from src.utils.logger import get_logger
from src.utils.user_lookup import get_user_by_email, get_user_by_phone

logger = get_logger("interface")


class LLMInterface:
    """streamlit interface wrapper."""

    def __init__(self, llm_model: str, temperature: float):
        """initialize the interface with agent."""
        if "agent" not in st.session_state:
            st.session_state.agent = create_agent(llm_model=llm_model, temperature=temperature)
        self.agent = st.session_state.agent

    def respond(self, message: str) -> str:
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

        # get current user_id from session state
        user_id = st.session_state.get("user_id")

        response = process_message(
            self.agent, message, conversation_history=conversation_history, user_id=user_id
        )
        return response

    def _identify_user(self, identifier: str) -> tuple[bool, str]:
        """identify user by phone or email. returns (success, message)."""
        # try phone first (e164 format)
        if identifier.startswith("+") or identifier.replace("-", "").replace(" ", "").isdigit():
            user = get_user_by_phone(identifier)
        else:
            # assume email
            user = get_user_by_email(identifier)
        
        if user:
            # extract user data from structured dict
            user_id = str(user.get("user_id"))
            email = user.get("email")
            phone = user.get("phone_e164")
            
            # set session state
            st.session_state.user_id = user_id
            st.session_state.user_identified = True
            
            # determine display name (prefer email, fallback to phone, then user id)
            display_name = email or phone or f"user {user_id[:8]}"
            st.session_state.user_display = display_name
            
            return True, f"welcome, {display_name}!"
        
        return False, "user not found. please check your phone number or email."

    def launch(self) -> None:
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

        # user identification (mock authentication)
        if "user_identified" not in st.session_state or not st.session_state.user_identified:
            # centered login form
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                st.title("Welcome")
                st.markdown("Please sign in to continue")
                st.markdown("<br>", unsafe_allow_html=True)
                
                identifier = st.text_input(
                    "Email or Phone Number",
                    placeholder="user@example.com or +1234567890",
                    key="user_identifier_input",
                    label_visibility="visible"
                )
                
                col_btn1, col_btn2 = st.columns([1, 1])
                with col_btn1:
                    if st.button("Sign In", type="primary", use_container_width=True, key="identify_user_btn"):
                        if identifier:
                            with st.spinner("Signing in..."):
                                success, message = self._identify_user(identifier)
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                        else:
                            st.warning("Please enter your email or phone number")
                
                with col_btn2:
                    if st.button("Demo Mode", use_container_width=True, key="test_user_btn"):
                        with st.spinner("Signing in..."):
                            success, message = self._identify_user("jack.yang@gatesfoundation.org")
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.caption("Prototype v0")
            
            return  # don't show chat until user is identified
        
        # main interface (after login)
        st.title("Self-Care Agent")
        
        # sidebar user info and actions
        with st.sidebar:
            st.markdown("### Account")
            if "user_id" in st.session_state:
                # get user info for display
                user_display = st.session_state.get("user_display", "User")
                st.markdown(f"**{user_display}**")
                st.caption(f"ID: {st.session_state.user_id[:8]}...")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Switch User", use_container_width=True):
                st.session_state.user_identified = False
                st.session_state.user_id = None
                st.session_state.user_display = None
                st.session_state.messages = []
                st.rerun()
            
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

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
