"""base channel handler class."""

import uuid
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

from src.agent import get_agent, process_message
from src.utils.context import correlation_id, channel


class BaseChannelHandler(ABC):
    """base class for channel handlers."""

    @property
    def agent(self):
        """get agent singleton from centralized factory."""
        return get_agent()

    @abstractmethod
    def get_conversation_history(
        self, user_id: Optional[str] = None
    ) -> List[Dict[str, str]]:
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
        user_timezone: Optional[str] = None,
        user_country: Optional[str] = None,
        channel_name: Optional[str] = None,
    ) -> tuple[str, list[dict[str, str]]]:
        """process user message and return response with sources.

        args:
            message: user message text
            user_id: optional user identifier (if not provided, uses get_user_id())
            user_age: optional user age for context
            user_gender: optional user gender for context
            user_timezone: optional user timezone for context
            user_country: optional country context for RAG filtering (e.g., "za", "ke")
            channel_name: optional channel name for logging (e.g., "streamlit", "whatsapp")

        returns:
            tuple of (agent response text, list of source dicts with title/content_type/similarity)
        """
        # generate unique correlation id for this request
        corr_id = str(uuid.uuid4())
        correlation_id.set(corr_id)

        # set channel context for logging
        if channel_name:
            channel.set(channel_name)

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
            user_country=user_country,
        )
        return response, sources
