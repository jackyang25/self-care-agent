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
        message: str,
        context: Optional[RequestContext] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> tuple[str, list[dict[str, str]], list[str]]:
        """process user message and return response with sources and tools.
        
        args:
            message: current user message
            context: request context object (if provided, takes precedence)
            messages: previous conversation history
            session_id: optional session identifier
            user_id: optional user identifier (used as session_id if session_id not provided)
            **kwargs: context fields (patient_id, literacy_level, primary_language, 
                     network_type, geospatial_tag, social_context, etc.)
        
        returns:
            tuple of (response text, rag sources, tools called)
        """
        # use user_id as session_id if session_id not provided
        if session_id is None:
            session_id = user_id

        # build context from kwargs if not provided
        if context is None and kwargs:
            context = RequestContext(**kwargs)

        return process_message(
            agent=self.agent,
            user_input=message,
            context=context,
            messages=messages,
            session_id=session_id,
        )
