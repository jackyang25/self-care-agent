"""database connection - lazy connection on first use."""

import os
import time
from contextlib import contextmanager
from typing import Dict, Any, Iterator
from psycopg2 import pool, OperationalError
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection, cursor

# connection pool (created on first use)
_connection_pool = None


def _get_connection_pool() -> pool.SimpleConnectionPool:
    """get or create connection pool with retry logic."""
    global _connection_pool
    if _connection_pool is None:
        db_config = {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": os.getenv("POSTGRES_PORT", "5432"),
            "database": os.getenv("POSTGRES_DB", "selfcare"),
            "user": os.getenv("POSTGRES_USER", "postgres"),
            "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
        }

        # retry connection with exponential backoff
        max_retries = 5
        retry_delay = 1
        for attempt in range(max_retries):
            try:
                _connection_pool = pool.SimpleConnectionPool(1, 10, **db_config)
                # test connection
                test_conn = _connection_pool.getconn()
                _connection_pool.putconn(test_conn)
                return _connection_pool
            except (OperationalError, Exception) as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2**attempt))
                    continue
                raise ConnectionError(
                    f"failed to connect to database after {max_retries} attempts: {e}"
                )

    return _connection_pool


@contextmanager
def get_db() -> Iterator[connection]:
    """get database connection (lazy - connects on first use)."""
    pool = _get_connection_pool()
    conn = pool.getconn()
    try:
        # validate connection is alive
        if conn.closed:
            conn = pool.getconn()
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


@contextmanager
def get_db_cursor() -> Iterator[cursor]:
    """get database cursor with dict-like rows."""
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur


def test_connection() -> Dict[str, Any]:
    """test database connection and return status info."""
    try:
        with get_db_cursor() as cur:
            cur.execute("SELECT version(), current_database(), current_user, now()")
            result = cur.fetchone()
            return {
                "connected": True,
                "database": result["current_database"],
                "user": result["current_user"],
                "postgres_version": result["version"].split(",")[0],
                "server_time": str(result["now"]),
            }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
        }
