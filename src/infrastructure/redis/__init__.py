"""redis cache layer - connection and conversation management."""

from src.infrastructure.redis.connection import (
    get_redis_client,
    get_redis_url,
    cache_set,
    cache_get,
    cache_delete,
    cache_exists,
    cache_expire,
    cache_get_many,
    cache_set_many,
    cache_clear_pattern,
)
from src.infrastructure.redis.conversation_manager import (
    get_conversation_history,
    add_message_to_history,
    save_conversation_history,
    clear_conversation_history,
    get_conversation_metadata,
)

__all__ = [
    "get_redis_client",
    "get_redis_url",
    "cache_set",
    "cache_get",
    "cache_delete",
    "cache_exists",
    "cache_expire",
    "cache_get_many",
    "cache_set_many",
    "cache_clear_pattern",
    "get_conversation_history",
    "add_message_to_history",
    "save_conversation_history",
    "clear_conversation_history",
    "get_conversation_metadata",
]
