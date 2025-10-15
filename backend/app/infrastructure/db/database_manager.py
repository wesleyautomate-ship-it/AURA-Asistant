"""
Database Connection Manager for Dubai Real Estate RAG System

This module provides robust database connection management with proper error handling,
connection pooling, and automatic cleanup to prevent application crashes.
"""

import logging
from contextlib import contextmanager
from typing import Generator, Optional
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError, OperationalError, DisconnectionError
from app.core.settings import DATABASE_URL

logger = logging.getLogger(__name__)

# Create database engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,  # Maximum number of connections in the pool
    max_overflow=20,  # Maximum number of connections that can be created beyond pool_size
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False,  # Set to True for SQL debugging
)


@contextmanager
def get_db_connection() -> Generator[Connection, None, None]:
    """
    Context manager for safe database connections.

    This function handles the full lifecycle of a database connection:
    - Opening the connection
    - Yielding it for use
    - Rolling back on error
    - Closing the connection in a finally block

    Usage:
        with get_db_connection() as conn:
            result = conn.execute(text("SELECT * FROM users"))
            return result.fetchall()
    """
    connection: Optional[Connection] = None
    try:
        # Get connection from pool
        connection = engine.connect()
        logger.debug("Database connection established")

        # Yield connection for use
        yield connection

        # Commit successful transaction
        connection.commit()
        logger.debug("Database transaction committed successfully")

    except (OperationalError, DisconnectionError) as e:
        # Handle connection/database errors
        logger.error(f"Database connection error: {e}")
        if connection:
            try:
                connection.rollback()
                logger.debug("Database transaction rolled back due to connection error")
            except Exception as rollback_error:
                logger.error(f"Failed to rollback transaction: {rollback_error}")
        raise HTTPException(status_code=503, detail="Database temporarily unavailable")

    except SQLAlchemyError as e:
        # Handle SQL errors
        logger.error(f"Database SQL error: {e}")
        if connection:
            try:
                connection.rollback()
                logger.debug("Database transaction rolled back due to SQL error")
            except Exception as rollback_error:
                logger.error(f"Failed to rollback transaction: {rollback_error}")
        raise HTTPException(status_code=500, detail="Database operation failed")

    except Exception as e:
        # Handle any other unexpected errors
        logger.error(f"Unexpected database error: {e}")
        if connection:
            try:
                connection.rollback()
                logger.debug("Database transaction rolled back due to unexpected error")
            except Exception as rollback_error:
                logger.error(f"Failed to rollback transaction: {rollback_error}")
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        # Always close the connection
        if connection:
            try:
                connection.close()
                logger.debug("Database connection closed")
            except Exception as close_error:
                logger.error(f"Failed to close database connection: {close_error}")


def check_database_health() -> dict:
    """
    Check database connection health.

    Returns:
        dict: Health status with connection details
    """
    try:
        with get_db_connection() as conn:
            # Test connection with simple query
            result = conn.execute(text("SELECT 1 as health_check"))
            result.fetchone()

            return {
                "status": "healthy",
                "message": "Database connection is working",
                "pool_size": engine.pool.size(),
                "checked_out": engine.pool.checkedout(),
            }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}",
            "pool_size": 0,
            "checked_out": 0,
        }


def get_database_stats() -> dict:
    """
    Get database connection pool statistics.

    Returns:
        dict: Database pool statistics
    """
    try:
        return {
            "pool_size": engine.pool.size(),
            "checked_out": engine.pool.checkedout(),
            "overflow": engine.pool.overflow(),
            "checked_in": engine.pool.checkedin(),
            "invalid": engine.pool.invalid(),
        }
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        return {
            "pool_size": 0,
            "checked_out": 0,
            "overflow": 0,
            "checked_in": 0,
            "invalid": 0,
            "error": str(e),
        }
