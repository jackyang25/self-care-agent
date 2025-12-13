"""execution context variables for request-scoped data."""

from typing import Optional
from contextvars import ContextVar

# user context
current_user_id: ContextVar[Optional[str]] = ContextVar("current_user_id", default=None)
current_user_age: ContextVar[Optional[int]] = ContextVar("current_user_age", default=None)
current_user_gender: ContextVar[Optional[str]] = ContextVar("current_user_gender", default=None)

