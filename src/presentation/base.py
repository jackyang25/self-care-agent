"""base channel handler class."""

from abc import ABC, abstractmethod
from typing import Optional

from src.application.agent import get_agent, process_message


class BaseChannelHandler(ABC):
    """base class for channel handlers."""

    @property
    def agent(self):
        """get agent singleton."""
        return get_agent()

    @abstractmethod
    def get_user_id(self) -> Optional[str]:
        """get current user id."""
        pass

    def respond(
        self,
        message: str,
        user_id: Optional[str] = None,
        user_age: Optional[int] = None,
        user_gender: Optional[str] = None,
        user_timezone: Optional[str] = None,
        user_country: Optional[str] = None,
    ) -> tuple[str, list[dict[str, str]], list[str]]:
        """process user message and return response with sources and tools."""
        if user_id is None:
            user_id = self.get_user_id()

        return process_message(
            agent=self.agent,
            user_input=message,
            user_id=user_id,
            user_age=user_age,
            user_gender=user_gender,
            user_timezone=user_timezone,
            user_country=user_country,
        )
