"""database connection using SQLAlchemy."""

import logging
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import Session, sessionmaker
from pgvector.psycopg2 import register_vector

from src.shared.config import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)

logger = logging.getLogger(__name__)

_engine = None
_session_factory = None


def _get_database_url() -> str:
    """construct database URL from environment variables."""
    return (
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )


def _get_engine():
    """get or create SQLAlchemy engine."""
    global _engine
    if _engine is None:
        database_url = _get_database_url()
        _engine = create_engine(
            database_url,
            pool_pre_ping=True,  # verify connections before using
            pool_size=5,
            max_overflow=10,
            echo=False,
        )

        # register pgvector types with psycopg2 on each connection
        @event.listens_for(_engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            register_vector(dbapi_conn)

        logger.info(f"database engine initialized: {database_url.split('@')[1]}")
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

    usage:
        with get_db_session() as session:
            users = session.query(User).all()
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


def test_connection() -> bool:
    """test database connection.

    returns:
        true if connection successful
    """
    try:
        engine = _get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("database connection test: success")
        return True
    except Exception as e:
        logger.error(f"database connection test failed: {e}")
        return False


def _get_connection_pool():
    """initialize connection pool (for compatibility with server warmup)."""
    return _get_engine()
