"""Lifespan management module for FastAPI application.

This module handles database connection setup and cleanup during application startup and shutdown.
It provides connection pooling and proper resource management for database interactions.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.cache import get_cache_manager, close_cache_manager
from app.web.settings import settings
from libs.postgresql_audit import sync_audit_triggers
from app.core.db.data_migrations.data_migration_init import initialize_data_migrations
from app.core.telemetry.setup import setup_sqlalchemy_instrumentation


@asynccontextmanager
async def lifespan_setup(app: FastAPI) -> AsyncGenerator[None]:
    """Initialize database connections and cleanup on shutdown.

    Args:
        app (FastAPI): The FastAPI application instance

    Yields:
        None

    Raises:
        SQLAlchemyError: If database connection or table creation fails
    """
    startup_start_time = datetime.now()
    logger.info("Starting application initialization")

    # Create engine with proper configuration
    engine: AsyncEngine = create_async_engine(
        settings.postgres_database_url,
        pool_size=20,
        max_overflow=10,
        pool_recycle=3600,
        echo=settings.postgres_database_echo,
    )

    # Create session factory with explicit type
    session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    # Initialize cache manager
    try:
        cache_manager = get_cache_manager()
        logger.info("Cache manager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize cache manager: {e!s}")
        raise

    # Store cache manager in app state
    app.state.cache_manager = cache_manager

    # Store in app state
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory

    # Initialize audit triggers using the session factory directly
    try:
        async with session_factory() as session:
            await sync_audit_triggers(session)
            logger.info("Audit trigger sync completed successfully")
    except Exception as e:
        logger.error(f"Error during audit trigger sync: {e!s}")

    # Initialize data migration system
    try:
        logger.info("Initializing data migration system...")
        await initialize_data_migrations(engine)
        logger.info("Data migration system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize data migration system: {e}")
        # Don't raise the exception to prevent application startup failure
        # The migration system will still work, just the table won't be auto-created
    # Set up SQLAlchemy instrumentation if telemetry is available
    if hasattr(app.state, 'telemetry') and app.state.telemetry:
        try:
            # For async engines, we need to instrument the sync engine
            setup_sqlalchemy_instrumentation(engine.sync_engine, app.state.telemetry)
            logger.info("SQLAlchemy instrumentation added successfully")
        except Exception as e:
            logger.warning(f"Could not instrument SQLAlchemy: {e}")
    else:
        logger.info("Skipping SQLAlchemy instrumentation - no telemetry config available")

    startup_elapsed_time = (datetime.now() - startup_start_time).total_seconds()
    logger.info(f"Application initialization completed in {startup_elapsed_time:.2f}s")

    yield

    # Cleanup
    logger.info("Starting application shutdown")
    shutdown_start_time = datetime.now()

    # Cleanup cache
    try:
        await close_cache_manager()
        logger.info("Cache connections closed successfully")
    except Exception as e:
        logger.error(f"Error during cache connection cleanup: {e!s}")

    try:
        await engine.dispose()
        logger.info("Database engine disposed successfully")
    except Exception as e:
        logger.error(f"Error disposing database engine: {e}")

    shutdown_elapsed_time = (datetime.now() - shutdown_start_time).total_seconds()
    logger.info(f"Application shutdown completed in {shutdown_elapsed_time:.2f}s")
