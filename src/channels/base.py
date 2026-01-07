"""base channel handler class."""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict

from src.application.agent import get_agent, process_message
from src.shared.schemas.context import RequestContext


class BaseChannelHandler(ABC):
    """base class for channel handlers."""

    @property
    def agent(self):
        """get agent singleton."""
        return get_agent()

    @abstractmethod
    def get_session_id(self) -> Optional[str]:
        """get current session id."""
        pass

    def respond(
        self,
        message: str,
        context: Optional[RequestContext] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        session_id: Optional[str] = None,
    ) -> tuple[str, list[dict[str, str]], list[str]]:
        """process user message and return response with sources and tools.
        
        args:
            message: current user message
            context: request context (age, gender, country, timezone)
            messages: previous conversation history from frontend
                      format: [{"role": "user", "content": "..."}, ...]
            session_id: optional session identifier
        
        returns:
            tuple of (response text, rag sources, tools called)
        """
        if session_id is None:
            session_id = self.get_session_id()

        return process_message(
            agent=self.agent,
            user_input=message,
            context=context,
            messages=messages,
            session_id=session_id,
        )
