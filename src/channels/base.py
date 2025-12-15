"""base channel handler class."""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from src.agent import create_agent, process_message


class BaseChannelHandler(ABC):
    """base class for channel handlers."""

    def __init__(self, llm_model: str, temperature: float):
        """initialize handler with agent configuration.
        
        args:
            llm_model: llm model name
            temperature: temperature setting
        """
        self.llm_model = llm_model
        self.temperature = temperature
        self._agent = None

    @property
    def agent(self):
        """get or create agent instance."""
        if self._agent is None:
            self._agent = create_agent(
                llm_model=self.llm_model, temperature=self.temperature
            )
        return self._agent

    @abstractmethod
    def get_conversation_history(self, user_id: Optional[str] = None) -> List[Dict[str, str]]:
        """get conversation history for user.
        
        args:
            user_id: user identifier
        
        returns:
            list of message dicts with 'role' and 'content'
        """
        pass

    @abstractmethod
    def get_user_id(self) -> Optional[str]:
        """get current user id.
        
        returns:
            user id if available, None otherwise
        """
        pass

    def respond(
        self, 
        message: str, 
        user_id: Optional[str] = None,
        user_age: Optional[int] = None,
        user_gender: Optional[str] = None,
        user_timezone: Optional[str] = None
    ) -> tuple[str, list[dict[str, str]]]:
        """process user message and return response with sources.
        
        args:
            message: user message text
            user_id: optional user identifier (if not provided, uses get_user_id())
            user_age: optional user age for context
            user_gender: optional user gender for context
            user_timezone: optional user timezone for context
        
        returns:
            tuple of (agent response text, list of source dicts with title/content_type/similarity)
        """
        # use provided user_id or get from channel-specific method
        if user_id is None:
            user_id = self.get_user_id()
        
        # get conversation history
        conversation_history = self.get_conversation_history(user_id=user_id)
        
        # process message through agent
        response, sources = process_message(
            agent=self.agent,
            user_input=message,
            conversation_history=conversation_history,
            user_id=user_id,
            user_age=user_age,
            user_gender=user_gender,
            user_timezone=user_timezone,
        )
        return response, sources

