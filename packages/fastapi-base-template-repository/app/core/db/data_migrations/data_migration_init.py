"""Data Migration Initialization Service.

This module provides functionality to automatically initialize the data migration
table when the application starts up.
"""

import configparser
import os
from pathlib import Path
from typing import Dict, Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from .data_migration_table import MigrationTable


class DataMigrationInitializer:
    """Handles automatic initialization of data migration system."""
    
    def __init__(self, config_path: str = "app/core/db/data_migrations/data_migration_config.ini"):
        """Initialize the data migration initializer.
        
        Args:
            config_path: Path to the migration configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        
        # Allow environment variable override for migration table name
        migration_table_name = os.getenv(
            'MIGRATION_TABLE_NAME', 
            self.config.get('migration_table_name', 'custom_migration_version')
        )
        
        self.migration_table = MigrationTable(table_name=migration_table_name)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file.
        
        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        config = configparser.ConfigParser(interpolation=None)  
        
        # Check if config file exists
        config_file = Path(self.config_path)
        if not config_file.exists():
            logger.warning(f"Data migration config file not found: {self.config_path}")
            return self._get_default_config()
        
        config.read(self.config_path)
        
        # Convert to dictionary
        config_dict = {}
        for section in config.sections():
            config_dict.update(dict(config.items(section)))
        
        return config_dict
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if config file is not found.
        
        Returns:
            Dict[str, Any]: Default configuration
        """
        return {
            'migration_table_name': os.getenv('MIGRATION_TABLE_NAME', 'custom_migration_version'),
            'script_location': 'app/core/db/data_migrations',
            'version_locations': 'app/core/db/data_migrations/versions',
            'level': 'INFO'
        }
    
    async def initialize_migration_table(self, engine: AsyncEngine) -> None:
        """Initialize the migration table if it doesn't exist.
        
        Args:
            engine: Database engine
        """
        try:
            async with engine.connect() as connection:
                # Check if table exists
                if not await self.migration_table.table_exists(connection):
                    logger.info("Creating data migration tracking table...")
                    await self.migration_table.create_table(connection)
                    logger.info(f"Data migration table '{self.migration_table.table_name}' created successfully")
                else:
                    logger.info(f"Data migration table '{self.migration_table.table_name}' already exists")
                    
        except Exception as e:
            logger.error(f"Failed to initialize data migration table: {e}")
            raise
    
    async def get_migration_status(self, engine: AsyncEngine) -> Dict[str, Any]:
        """Get current migration status.
        
        Args:
            engine: Database engine
            
        Returns:
            Dict[str, Any]: Migration status information
        """
        try:
            async with engine.connect() as connection:
                applied_migrations = await self.migration_table.get_applied_migrations(connection)
                current_head = await self.migration_table.get_current_head(connection)
                
                return {
                    'table_exists': await self.migration_table.table_exists(connection),
                    'applied_migrations_count': len(applied_migrations),
                    'current_head': current_head,
                    'applied_migrations': applied_migrations
                }
        except Exception as e:
            logger.error(f"Failed to get migration status: {e}")
            return {
                'table_exists': False,
                'applied_migrations_count': 0,
                'current_head': None,
                'applied_migrations': [],
                'error': str(e)
            }
    
    async def ensure_versions_directory(self) -> None:
        """Ensure the versions directory exists."""
        versions_path = Path(self.config.get('version_locations', 'app/core/db/data_migrations/versions'))
        if not versions_path.exists():
            versions_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created versions directory: {versions_path}")
            
            # Create __init__.py file
            init_file = versions_path / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""Data migration versions."""\n')
                logger.info("Created __init__.py in versions directory")


# Singleton instance for easy import
data_migration_initializer = DataMigrationInitializer()


async def initialize_data_migrations(engine: AsyncEngine) -> None:
    """Initialize data migrations system.
    
    This is a convenience function that can be called during application startup.
    
    Args:
        engine: Database engine
    """
    await data_migration_initializer.ensure_versions_directory()
    await data_migration_initializer.initialize_migration_table(engine)
    
    # Log migration status
    status = await data_migration_initializer.get_migration_status(engine)
    logger.info(f"Data migration status: {status}")


async def get_migration_status(engine: AsyncEngine) -> Dict[str, Any]:
    """Get current migration status.
    
    Args:
        engine: Database engine
        
    Returns:
        Dict[str, Any]: Migration status information
    """
    return await data_migration_initializer.get_migration_status(engine) 