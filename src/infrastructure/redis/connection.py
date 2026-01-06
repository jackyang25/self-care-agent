"""redis client for caching and session management."""

import os
import json
from typing import Optional, Any
import redis
from redis.connection import ConnectionPool

# redis connection pool (created on first use)
_redis_pool = None


def _get_redis_pool() -> ConnectionPool:
    """get or create redis connection pool."""
    global _redis_pool
    if _redis_pool is None:
        redis_config = {
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": int(os.getenv("REDIS_PORT", "6379")),
            "db": int(os.getenv("REDIS_DB", "0")),
            "decode_responses": True,
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
        }
        
        # add password if provided
        password = os.getenv("REDIS_PASSWORD")
        if password:
            redis_config["password"] = password
        
        _redis_pool = ConnectionPool(**redis_config)
    
    return _redis_pool


def get_redis_client() -> redis.Redis:
    """get redis client from connection pool.
    
    returns:
        redis client instance
    """
    pool = _get_redis_pool()
    return redis.Redis(connection_pool=pool)


def get_redis_url() -> str:
    """get redis connection URL.
    
    returns:
        redis connection URL string
    """
    host = os.getenv("REDIS_HOST", "localhost")
    port = os.getenv("REDIS_PORT", "6379")
    db = os.getenv("REDIS_DB", "0")
    password = os.getenv("REDIS_PASSWORD")
    
    if password:
        return f"redis://:{password}@{host}:{port}/{db}"
    return f"redis://{host}:{port}/{db}"


def cache_set(
    key: str,
    value: Any,
    ttl: Optional[int] = None,
    serialize: bool = True,
) -> bool:
    """set a value in cache with optional expiration.
    
    args:
        key: cache key
        value: value to cache (will be JSON serialized if serialize=True)
        ttl: time-to-live in seconds (None = no expiration)
        serialize: whether to JSON serialize the value
    
    returns:
        True if successful, False otherwise
    """
    try:
        client = get_redis_client()
        data = json.dumps(value) if serialize else value
        
        if ttl:
            return client.setex(key, ttl, data)
        else:
            return client.set(key, data)
    except Exception:
        return False


def cache_get(
    key: str,
    deserialize: bool = True,
) -> Optional[Any]:
    """get a value from cache.
    
    args:
        key: cache key
        deserialize: whether to JSON deserialize the value
    
    returns:
        cached value or None if not found/error
    """
    try:
        client = get_redis_client()
        data = client.get(key)
        
        if data is None:
            return None
        
        return json.loads(data) if deserialize else data
    except Exception:
        return None


def cache_delete(key: str) -> bool:
    """delete a key from cache.
    
    args:
        key: cache key to delete
    
    returns:
        True if key was deleted, False otherwise
    """
    try:
        client = get_redis_client()
        return client.delete(key) > 0
    except Exception:
        return False


def cache_exists(key: str) -> bool:
    """check if a key exists in cache.
    
    args:
        key: cache key to check
    
    returns:
        True if key exists, False otherwise
    """
    try:
        client = get_redis_client()
        return client.exists(key) > 0
    except Exception:
        return False


def cache_expire(key: str, ttl: int) -> bool:
    """set expiration on an existing key.
    
    args:
        key: cache key
        ttl: time-to-live in seconds
    
    returns:
        True if expiration was set, False otherwise
    """
    try:
        client = get_redis_client()
        return client.expire(key, ttl)
    except Exception:
        return False


def cache_get_many(keys: list[str], deserialize: bool = True) -> dict[str, Any]:
    """get multiple values from cache.
    
    args:
        keys: list of cache keys
        deserialize: whether to JSON deserialize values
    
    returns:
        dict mapping keys to values (None for missing keys)
    """
    try:
        client = get_redis_client()
        values = client.mget(keys)
        
        result = {}
        for key, value in zip(keys, values):
            if value is not None:
                result[key] = json.loads(value) if deserialize else value
            else:
                result[key] = None
        
        return result
    except Exception:
        return {key: None for key in keys}


def cache_set_many(
    mapping: dict[str, Any],
    ttl: Optional[int] = None,
    serialize: bool = True,
) -> bool:
    """set multiple key-value pairs in cache.
    
    args:
        mapping: dict of key-value pairs to cache
        ttl: time-to-live in seconds (applied to all keys)
        serialize: whether to JSON serialize values
    
    returns:
        True if successful, False otherwise
    """
    try:
        client = get_redis_client()
        
        # serialize values if needed
        data = {}
        for key, value in mapping.items():
            data[key] = json.dumps(value) if serialize else value
        
        # set all values
        client.mset(data)
        
        # apply ttl if provided
        if ttl:
            for key in data.keys():
                client.expire(key, ttl)
        
        return True
    except Exception:
        return False


def cache_clear_pattern(pattern: str) -> int:
    """delete all keys matching a pattern.
    
    args:
        pattern: redis key pattern (e.g., "user:*", "session:*")
    
    returns:
        number of keys deleted
    """
    try:
        client = get_redis_client()
        keys = client.keys(pattern)
        if keys:
            return client.delete(*keys)
        return 0
    except Exception:
        return 0

