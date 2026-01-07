"""base channel handler class."""

from abc import ABC
from typing import Optional, List, Dict

from src.application.agent import get_agent, process_message
from src.shared.schemas.context import RequestContext


class BaseChannelHandler(ABC):
    """base class for channel handlers."""

    @property
    def agent(self):
        """get agent singleton."""
        return get_agent()

    def respond(
        self,
        user_message: str,
        context: Optional[RequestContext] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> tuple[str, list[dict[str, str]], list[str]]:
        """process user message and return response with sources and tools.
        
        args:
            user_message: current user message (required)
            context: pre-built RequestContext object (optional, will be built from kwargs if not provided)
            conversation_history: previous conversation messages for multi-turn context 
                                 (optional, list of {"role": "user/assistant", "content": "..."})
            **kwargs: context fields that will be automatically mapped to RequestContext 
                     (whatsapp_id, patient_id, literacy_level, primary_language, 
                     network_type, geospatial_tag, social_context, patient_age, 
                     patient_gender, active_diagnoses, current_medications, allergies, 
                     latest_vitals, adherence_score, refill_due_date, etc.)
        
        returns:
            tuple of (response text, rag sources, tools called)
        """
        # build context from kwargs if not provided
        if context is None and kwargs:
            context = RequestContext(**kwargs)

        return process_message(
            agent=self.agent,
            user_message=user_message,
            context=context,
            conversation_history=conversation_history,
        )
