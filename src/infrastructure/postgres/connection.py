"""database connection - lazy connection on first use."""

import os
import time
from contextlib import contextmanager
from typing import Dict, Any, Iterator
from psycopg2 import pool, OperationalError
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection, cursor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

import logging

logger = logging.getLogger(__name__)

# connection pool (created on first use)
_connection_pool = None

# sqlalchemy engine and session factory
_engine = None
_session_factory = None


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
                
                logger.info(f"postgres connection pool initialized | host={db_config['host']} | port={db_config['port']} | db={db_config['database']}")
                return _connection_pool
            except (OperationalError, Exception) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"attempt {attempt + 1}/{max_retries} failed - retrying...")
                    time.sleep(retry_delay * (2**attempt))
                    continue
                logger.error(f"INIT: POSTGRES | FAILED after {max_retries} attempts: {e}")
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


def _get_database_url() -> str:
    """construct database URL for SQLAlchemy."""
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "selfcare")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"


def _get_engine():
    """get or create SQLAlchemy engine."""
    global _engine
    if _engine is None:
        database_url = _get_database_url()
        _engine = create_engine(
            database_url,
            poolclass=NullPool,
            echo=False,
        )
        logger.info(f"sqlalchemy engine initialized | url={database_url.split('@')[1]}")
    return _engine


def _get_session_factory():
    """get or create session factory."""
    global _session_factory
    if _session_factory is None:
        engine = _get_engine()
        _session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    return _session_factory


@contextmanager
def get_db_session() -> Iterator[Session]:
    """get database session for ORM operations.
    
    Usage:
        with get_db_session() as session:
            user = session.query(User).filter_by(email='test@example.com').first()
    """
    session_factory = _get_session_factory()
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
