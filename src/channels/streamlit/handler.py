"""streamlit channel handler - core logic only."""

import logging
import time

import streamlit as st

from src.channels.base import BaseChannelHandler

logger = logging.getLogger(__name__)

class _InMemoryLogHandler(logging.Handler):
    """Capture selected log lines in-memory for UI audit display."""

    def __init__(self) -> None:
        super().__init__(level=logging.INFO)
        self.lines: list[str] = []
        self._formatter = logging.Formatter(
            "[%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d:%(funcName)s] %(message)s"
        )

    def emit(self, record: logging.LogRecord) -> None:
        try:
            name = record.name or ""
            # Keep this tight: only capture app workflow and key infra/http calls
            allowed = (
                name.startswith("src.application.agent")
                or name.startswith("src.infrastructure.postgres")
                or name.startswith("httpx")
            )
            if not allowed:
                return
            self.lines.append(self._formatter.format(record))
        except Exception:
            # Never break the app due to logging capture
            return


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

        # Capture a per-turn workflow trace for the UI (read-only).
        mem_handler = _InMemoryLogHandler()
        root_logger = logging.getLogger()
        root_logger.addHandler(mem_handler)

        t0 = time.perf_counter()

        try:
            def _truncate(text: object, limit: int = 500) -> str:
                """Truncate text for audit display (avoid giant session payloads)."""
                s = "" if text is None else str(text)
                return (s[:limit] + "…") if len(s) > limit else s

            # prepare refill date as string if present
            refill_date = st.session_state.get("refill_due_date")
            refill_date_str = refill_date.isoformat() if refill_date else None

            # get conversation history (exclude the current message we're responding to)
            history = (
                st.session_state.messages[:-1]
                if len(st.session_state.messages) > 1
                else None
            )

            # capture the raw payload we pass to the agent (for UI audit only)
            # note: this is read-only metadata and does not change agent behavior.
            audit_config = {
                "whatsapp_id": st.session_state.get("whatsapp_id"),
                "patient_id": st.session_state.get("emr_patient_id"),
                "literacy_level": st.session_state.get("literacy_level"),
                "primary_language": st.session_state.get("primary_language"),
                "network_type": st.session_state.get("network_type"),
                "geospatial_tag": st.session_state.get("geospatial_tag"),
                "social_context": st.session_state.get("social_context"),
                "patient_age": st.session_state.get("patient_age"),
                "patient_gender": st.session_state.get("patient_gender"),
                "active_diagnoses": st.session_state.get("active_diagnoses"),
                "current_medications": st.session_state.get("current_medications"),
                "allergies": st.session_state.get("allergies"),
                "latest_vitals": st.session_state.get("latest_vitals"),
                "adherence_score": st.session_state.get("adherence_score"),
                "refill_due_date": refill_date_str,
            }

            audit_conversation_history = []
            if history:
                # Only snapshot role+content; keep it bounded to avoid runaway memory.
                # This matches the structure expected by `conversation_history`.
                for msg in history[-20:]:
                    audit_conversation_history.append(
                        {
                            "role": msg.get("role"),
                            "content": _truncate(msg.get("content")),
                        }
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

            elapsed_ms = int((time.perf_counter() - t0) * 1000)
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response,
                    "tools": tools,
                    "sources": sources,
                    "audit_logs": list(mem_handler.lines),
                    "audit_payload": {
                        "user_message": _truncate(prompt, limit=1000),
                        "conversation_history": audit_conversation_history,
                        "conversation_history_len": len(history) if history else 0,
                        "config": audit_config,
                    },
                    "audit_metrics": {
                        "elapsed_ms": elapsed_ms,
                        "tools_count": len(tools or []),
                        "sources_count": len(sources or []),
                        "history_len": len(history) if history else 0,
                    },
                }
            )

        except Exception as e:
            logger.exception("agent response failed")
            elapsed_ms = int((time.perf_counter() - t0) * 1000)
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": f"Sorry — I ran into an error while responding: {str(e)}",
                    "tools": [],
                    "sources": [],
                    "audit_logs": list(mem_handler.lines),
                    "audit_payload": {
                        "user_message": prompt,
                        "conversation_history_len": len(st.session_state.messages[:-1])
                        if len(st.session_state.messages) > 1
                        else 0,
                    },
                    "audit_metrics": {"elapsed_ms": elapsed_ms},
                }
            )
        finally:
            try:
                root_logger.removeHandler(mem_handler)
            except Exception:
                pass

        st.session_state.processing = False
        st.rerun()
