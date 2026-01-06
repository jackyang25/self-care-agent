"""custom conversation history manager for healthcare compliance.

stores conversation history in redis with full control over data format,
encryption, and audit trails for PHI compliance.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from src.infrastructure.redis.connection import (
    get_redis_client,
    cache_set,
    cache_get,
    cache_delete,
)
from src.shared.logger import get_logger

logger = get_logger("infrastructure.cache.conversation")

# conversation TTL: 24 hours (86400 seconds)
CONVERSATION_TTL = 86400


def _serialize_message(message) -> Dict:
    """serialize langchain message to dict for redis storage.
    
    args:
        message: langchain message object
    
    returns:
        serializable dict with type, content, and metadata
    """
    msg_dict = {
        "type": message.__class__.__name__,
        "content": message.content,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    # preserve additional attributes for different message types
    if isinstance(message, AIMessage):
        if hasattr(message, "tool_calls") and message.tool_calls:
            msg_dict["tool_calls"] = message.tool_calls
    elif isinstance(message, ToolMessage):
        if hasattr(message, "tool_call_id"):
            msg_dict["tool_call_id"] = message.tool_call_id
    
    # preserve any additional kwargs
    if hasattr(message, "additional_kwargs") and message.additional_kwargs:
        msg_dict["additional_kwargs"] = message.additional_kwargs
    
    return msg_dict


def _deserialize_message(msg_dict: Dict):
    """deserialize dict from redis to langchain message.
    
    args:
        msg_dict: serialized message dict
    
    returns:
        langchain message object
    """
    msg_type = msg_dict.get("type")
    content = msg_dict.get("content", "")
    
    if msg_type == "HumanMessage":
        return HumanMessage(content=content)
    elif msg_type == "AIMessage":
        kwargs = {}
        if "tool_calls" in msg_dict:
            kwargs["tool_calls"] = msg_dict["tool_calls"]
        if "additional_kwargs" in msg_dict:
            kwargs["additional_kwargs"] = msg_dict["additional_kwargs"]
        return AIMessage(content=content, **kwargs)
    elif msg_type == "SystemMessage":
        return SystemMessage(content=content)
    elif msg_type == "ToolMessage":
        kwargs = {}
        if "tool_call_id" in msg_dict:
            kwargs["tool_call_id"] = msg_dict["tool_call_id"]
        return ToolMessage(content=content, **kwargs)
    else:
        # fallback to human message
        logger.warning(f"unknown message type: {msg_type}, treating as HumanMessage")
        return HumanMessage(content=content)


def get_conversation_history(user_id: str) -> List:
    """get conversation history for user.
    
    args:
        user_id: user identifier
    
    returns:
        list of langchain message objects
    """
    if not user_id:
        return []
    
    try:
        key = f"conversation:{user_id}"
        data = cache_get(key, deserialize=True)
        
        if not data or not isinstance(data, list):
            return []
        
        # deserialize messages
        messages = []
        for msg_dict in data:
            try:
                msg = _deserialize_message(msg_dict)
                messages.append(msg)
            except Exception as e:
                logger.error(f"failed to deserialize message: {e}")
                continue
        
        logger.debug(f"retrieved {len(messages)} messages for user {user_id[:8]}...")
        return messages
    
    except Exception as e:
        logger.error(f"failed to get conversation history: {e}")
        return []


def add_message_to_history(user_id: str, message) -> bool:
    """add a message to user's conversation history.
    
    args:
        user_id: user identifier
        message: langchain message object
    
    returns:
        True if successful, False otherwise
    """
    if not user_id:
        return False
    
    try:
        key = f"conversation:{user_id}"
        
        # get existing history
        history = cache_get(key, deserialize=True) or []
        
        # serialize and append new message
        msg_dict = _serialize_message(message)
        history.append(msg_dict)
        
        # save back to redis with TTL
        success = cache_set(key, history, ttl=CONVERSATION_TTL, serialize=True)
        
        if success:
            logger.debug(f"added message to conversation for user {user_id[:8]}...")
        
        return success
    
    except Exception as e:
        logger.error(f"failed to add message to history: {e}")
        return False


def save_conversation_history(user_id: str, messages: List) -> bool:
    """save complete conversation history for user (replaces existing).
    
    args:
        user_id: user identifier
        messages: list of langchain message objects
    
    returns:
        True if successful, False otherwise
    """
    if not user_id:
        return False
    
    try:
        key = f"conversation:{user_id}"
        
        # serialize all messages
        serialized = [_serialize_message(msg) for msg in messages]
        
        # save to redis with TTL
        success = cache_set(key, serialized, ttl=CONVERSATION_TTL, serialize=True)
        
        if success:
            logger.info(f"saved {len(messages)} messages for user {user_id[:8]}...")
        
        return success
    
    except Exception as e:
        logger.error(f"failed to save conversation history: {e}")
        return False


def clear_conversation_history(user_id: str) -> bool:
    """clear conversation history for a user.
    
    args:
        user_id: user identifier
    
    returns:
        True if successful, False otherwise
    """
    if not user_id:
        return False
    
    try:
        key = f"conversation:{user_id}"
        success = cache_delete(key)
        
        if success:
            logger.info(f"cleared conversation history for user {user_id[:8]}...")
        
        return success
    
    except Exception as e:
        logger.error(f"failed to clear conversation history: {e}")
        return False


def get_conversation_metadata(user_id: str) -> Optional[Dict]:
    """get metadata about user's conversation.
    
    args:
        user_id: user identifier
    
    returns:
        dict with message_count, first_message_time, last_message_time
    """
    if not user_id:
        return None
    
    try:
        key = f"conversation:{user_id}"
        data = cache_get(key, deserialize=True)
        
        if not data or not isinstance(data, list):
            return None
        
        metadata = {
            "message_count": len(data),
            "first_message_time": data[0].get("timestamp") if data else None,
            "last_message_time": data[-1].get("timestamp") if data else None,
        }
        
        return metadata
    
    except Exception as e:
        logger.error(f"failed to get conversation metadata: {e}")
        return None
