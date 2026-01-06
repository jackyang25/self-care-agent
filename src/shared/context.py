"""execution context for request-scoped data."""

from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import pytz

# thread-local context variables (set by execution_node, accessed by tools)
current_user_id: ContextVar[Optional[str]] = ContextVar("current_user_id", default=None)
current_user_age: ContextVar[Optional[int]] = ContextVar("current_user_age", default=None)
current_user_gender: ContextVar[Optional[str]] = ContextVar("current_user_gender", default=None)
current_user_timezone: ContextVar[Optional[str]] = ContextVar("current_user_timezone", default="UTC")
current_user_country: ContextVar[Optional[str]] = ContextVar("current_user_country", default=None)
current_node: ContextVar[Optional[str]] = ContextVar("current_node", default=None)


@dataclass
class UserContext:
    """user context for agent execution.
    
    encapsulates user data for state management in langgraph.
    synced to context vars before tool execution.
    """
    
    user_id: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    timezone: str = "UTC"
    country: Optional[str] = None
    
    def to_dict(self) -> dict:
        """convert to dict for serialization."""
        return {
            "user_id": self.user_id,
            "age": self.age,
            "gender": self.gender,
            "timezone": self.timezone,
            "country": self.country,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "UserContext":
        """create from dict."""
        return cls(
            user_id=data.get("user_id"),
            age=data.get("age"),
            gender=data.get("gender"),
            timezone=data.get("timezone", "UTC"),
            country=data.get("country"),
        )
    
    def build_patient_context_section(self) -> str:
        """build patient context section for system prompt."""
        context_parts = []
        
        # add current time in user's timezone
        try:
            tz = pytz.timezone(self.timezone) if self.timezone else pytz.UTC
            current_time = datetime.now(tz)
            time_str = current_time.strftime("%A, %B %d, %Y at %I:%M %p %Z")
        except Exception:
            current_time = datetime.now(pytz.UTC)
            time_str = current_time.strftime("%A, %B %d, %Y at %I:%M %p UTC")
        
        context_parts.append(f"Current time: {time_str}")
        
        if self.age is not None:
            context_parts.append(f"Age: {self.age}")
        if self.gender is not None:
            context_parts.append(f"Gender: {self.gender}")
        if self.country is not None:
            context_parts.append(f"Country: {self.country}")
        
        if not context_parts:
            return ""
        
        context_lines = "\n".join(f"- {part}" for part in context_parts)
        return (
            f"\n\n## current patient context\n\n{context_lines}\n\n"
            f"use this information to provide appropriate, personalized care. "
            f"use the current time to schedule appointments appropriately "
            f"(e.g., 'tomorrow' means the next day from current time). "
            f"when using rag_retrieval, country-specific clinical guidelines will be prioritized."
        )

