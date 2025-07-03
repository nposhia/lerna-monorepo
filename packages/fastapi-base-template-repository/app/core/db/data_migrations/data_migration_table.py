"""Migration table management for tracking applied migrations.

This module handles the database table that tracks which migrations have been applied.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, MetaData, String, Table, text
from sqlalchemy.ext.asyncio import AsyncConnection


class MigrationTable:
    """Manages the migration tracking table."""
    
    def __init__(self, table_name: str = "custom_migration_version"):
        """Initialize migration table manager.
        
        Args:
            table_name: Name of the migration tracking table
        """
        self.table_name = table_name
        self.metadata = MetaData()
        
        # Define the migration table schema
        self.table = Table(
            table_name,
            self.metadata,
            Column("version_num", String(36), primary_key=True, nullable=False),
            Column("applied_at", DateTime, nullable=False, default=datetime.utcnow),
            Column("description", String(255), nullable=True),
        )
    
    async def create_table(self, connection: AsyncConnection) -> None:
        """Create the migration table if it doesn't exist.
        
        Args:
            connection: Database connection
        """
        await connection.run_sync(self.metadata.create_all)
        await connection.commit()
    
    async def table_exists(self, connection: AsyncConnection) -> bool:
        """Check if the migration table exists.
        
        Args:
            connection: Database connection
            
        Returns:
            bool: True if table exists, False otherwise
        """
        result = await connection.execute(
            text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{self.table_name}'
                );
            """)
        )
        return result.scalar()
    
    async def get_applied_migrations(self, connection: AsyncConnection) -> List[str]:
        """Get list of applied migration versions.
        
        Args:
            connection: Database connection
            
        Returns:
            List[str]: List of applied migration version numbers
        """
        if not await self.table_exists(connection):
            return []
            
        result = await connection.execute(
            text(f"SELECT version_num FROM {self.table_name} ORDER BY applied_at")
        )
        return [row[0] for row in result.fetchall()]
    
    async def mark_migration_applied(
        self, 
        connection: AsyncConnection, 
        version: str, 
        description: Optional[str] = None
    ) -> None:
        """Mark a migration as applied.
        
        Args:
            connection: Database connection
            version: Migration version number
            description: Optional migration description
        """
        await connection.execute(
            text(f"""
                INSERT INTO {self.table_name} (version_num, applied_at, description)
                VALUES (:version, :applied_at, :description)
            """),
            {
                "version": version,
                "applied_at": datetime.utcnow(),
                "description": description
            }
        )
        await connection.commit()
    
    async def unmark_migration_applied(
        self, 
        connection: AsyncConnection, 
        version: str
    ) -> None:
        """Remove a migration from applied list.
        
        Args:
            connection: Database connection
            version: Migration version number
        """
        await connection.execute(
            text(f"DELETE FROM {self.table_name} WHERE version_num = :version"),
            {"version": version}
        )
        await connection.commit()
    
    async def get_current_head(self, connection: AsyncConnection) -> Optional[str]:
        """Get the current head migration version.
        
        Args:
            connection: Database connection
            
        Returns:
            Optional[str]: Current head version or None if no migrations applied
        """
        if not await self.table_exists(connection):
            return None
            
        result = await connection.execute(
            text(f"""
                SELECT version_num FROM {self.table_name} 
                ORDER BY applied_at DESC LIMIT 1
            """)
        )
        row = result.fetchone()
        return row[0] if row else None