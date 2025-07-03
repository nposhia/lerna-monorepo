"""Database Session Manager.

This module is responsible for managing database sessions and providing dependency injection
for database access throughout the application.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession]:
    """Dependency method that yields an async database session.

    Args:
        request: FastAPI request object containing the database session factory

    Yields:
        AsyncSession: Database session for performing database operations
    """
    session = request.app.state.db_session_factory()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

# Type alias for dependency injection using the class method
DbSession = Annotated[AsyncSession, Depends(get_db_session)]
