"""Script to synchronize audit triggers.

This script handles the synchronization of audit triggers for all auditable tables.
It can be run directly or via the Makefile.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.web.settings import settings
from libs.postgresql_audit import sync_audit_triggers


async def main() -> None:
    """Main function to sync audit triggers."""
    logger.info("Starting audit trigger synchronization script...")
    
    # Create database engine
    engine: AsyncEngine = create_async_engine(
        settings.postgres_database_url,
        pool_size=5,
        max_overflow=5,
        pool_recycle=3600,
        echo=settings.postgres_database_echo,
    )
    
    # Create session factory
    session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    
    try:
        # Sync audit triggers
        async with session_factory() as session:
            await sync_audit_triggers(session)
        
        logger.info("Audit trigger synchronization completed successfully")
        
    except Exception as e:
        logger.error(f"Error during audit trigger synchronization: {e!s}")
        sys.exit(1)
    finally:
        # Cleanup database connection
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main()) 