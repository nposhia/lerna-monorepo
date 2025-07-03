"""Audit service for managing database audit triggers.

This module provides functionality to sync audit triggers for SQLModel tables
that are marked as auditable, and manage individual table audit triggers.
"""

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import sqlalchemy as sa

# Import all your models so they are registered
from app.core.models import *


async def sync_audit_triggers(db: AsyncSession) -> None:
    """
    Compares all SQLModel tables with the `__auditable__` flag against the
    database to see which ones are missing an audit trigger, and attaches it.
    Also removes triggers from tables that should no longer be audited.
    
    Args:
        db: Database session for executing the sync operations
    """
    logger.info("Starting audit trigger synchronization...")

    # --- 1. Get the list of tables that SHOULD have a trigger ---
    tables_that_should_be_audited = set()

    def find_all_subclasses(cls):
        all_subclasses = []
        for subclass in cls.__subclasses__():
            all_subclasses.append(subclass)
            all_subclasses.extend(find_all_subclasses(subclass))
        return all_subclasses

    for model_class in find_all_subclasses(SQLModel):
        if getattr(model_class, '__auditable__', False) and hasattr(model_class, '__tablename__'):
            tables_that_should_be_audited.add(model_class.__tablename__)

    # --- 2. Get the list of tables that CURRENTLY HAVE the trigger ---
    query = """
        SELECT event_object_table
        FROM information_schema.triggers
        WHERE trigger_name LIKE 'audit_trigger_for_%';
    """
    result = await db.execute(sa.text(query))
    tables_that_are_audited = {row[0] for row in result.fetchall()}

    # --- 3. Find tables to ADD triggers to ---
    tables_to_add_trigger_to = tables_that_should_be_audited - tables_that_are_audited

    # --- 4. Find tables to REMOVE triggers from ---
    tables_to_remove_trigger_from = tables_that_are_audited - tables_that_should_be_audited

    # --- 5. Handle trigger removal ---
    if tables_to_remove_trigger_from:
        logger.info(f"Found {len(tables_to_remove_trigger_from)} tables with triggers that should be removed: {tables_to_remove_trigger_from}")
        
        for table_name in tables_to_remove_trigger_from:
            logger.info(f"Removing audit trigger from table: {table_name}")
            await db.execute(sa.text(f"SELECT teardown_audit_for_table('{table_name}');"))

    # --- 6. Handle trigger addition ---
    if tables_to_add_trigger_to:
        logger.info(f"Found {len(tables_to_add_trigger_to)} tables missing audit triggers: {tables_to_add_trigger_to}")

        for table_name in tables_to_add_trigger_to:
            logger.info(f"Attaching audit trigger to table: {table_name}")
            await db.execute(sa.text(f"SELECT setup_audit_for_table('{table_name}');"))

    # --- 7. Final status ---
    if not tables_to_add_trigger_to and not tables_to_remove_trigger_from:
        if not tables_that_should_be_audited:
            logger.info("No models marked as auditable.")
        else:
            logger.info("All auditable tables already have triggers, and no unwanted triggers found. Synchronization complete.")
    else:
        await db.commit()
        logger.info("Successfully synchronized all audit triggers.")


async def remove_audit_trigger_for_table(db: AsyncSession, table_name: str) -> bool:
    """
    Manually remove audit trigger from a specific table.
    
    Args:
        db: Database session
        table_name: Name of the table to remove trigger from
        
    Returns:
        True if trigger was removed successfully, False if no trigger existed
    """
    logger.info(f"Manually removing audit trigger from table: {table_name}")
    
    # Check if trigger exists first
    query = """
        SELECT COUNT(*)
        FROM information_schema.triggers
        WHERE trigger_name = %s AND event_object_table = %s;
    """
    result = await db.execute(sa.text(query), (f'audit_trigger_for_{table_name}', table_name))
    trigger_exists = result.scalar() > 0
    
    if not trigger_exists:
        logger.warning(f"No audit trigger found for table: {table_name}")
        return False
    
    # Remove the trigger
    await db.execute(sa.text(f"SELECT teardown_audit_for_table('{table_name}');"))
    await db.commit()
    
    logger.info(f"Successfully removed audit trigger from table: {table_name}")
    return True


async def add_audit_trigger_for_table(db: AsyncSession, table_name: str) -> bool:
    """
    Manually add audit trigger to a specific table.
    
    Args:
        db: Database session
        table_name: Name of the table to add trigger to
        
    Returns:
        True if trigger was added successfully, False if trigger already existed
    """
    logger.info(f"Manually adding audit trigger to table: {table_name}")
    
    # Check if trigger already exists
    query = """
        SELECT COUNT(*)
        FROM information_schema.triggers
        WHERE trigger_name = %s AND event_object_table = %s;
    """
    result = await db.execute(sa.text(query), (f'audit_trigger_for_{table_name}', table_name))
    trigger_exists = result.scalar() > 0
    
    if trigger_exists:
        logger.warning(f"Audit trigger already exists for table: {table_name}")
        return False
    
    # Add the trigger
    await db.execute(sa.text(f"SELECT setup_audit_for_table('{table_name}');"))
    await db.commit()
    
    logger.info(f"Successfully added audit trigger to table: {table_name}")
    return True 