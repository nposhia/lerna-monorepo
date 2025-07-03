"""Migration runner and CLI interface for the custom migration system.

This module provides the command-line interface and execution context for migrations.
"""

import argparse
import asyncio
import configparser
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection

from .data_migration_commands import MigrationCommands
from app.web.settings import settings


class MigrationContext:
    """Context object passed to migration functions."""
    
    def __init__(self, connection: AsyncConnection, config: Dict[str, Any]):
        """Initialize migration context.
        
        Args:
            connection: Database connection
            config: Migration configuration
        """
        self.connection = connection
        self.config = config
    
    async def execute(self, sql: str, parameters: Optional[Dict[str, Any]] = None) -> None:
        """Execute SQL statement.
        
        Args:
            sql: SQL statement to execute
            parameters: Optional parameters for the SQL statement
            
        Raises:
            Exception: If SQL execution fails
        """
        from sqlalchemy import text
        
        try:
            await self.connection.execute(text(sql), parameters or {})
        except Exception as e:
            # Provide more context about the failed SQL
            raise Exception(f"SQL execution failed: {sql}\nError: {str(e)}") from e
    
    async def execute_script(self, sql_script: str) -> None:
        """Execute a multi-statement SQL script.
        
        Args:
            sql_script: SQL script with multiple statements
            
        Raises:
            Exception: If any SQL statement execution fails
        """
        statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements, 1):
            try:
                await self.execute(statement)
            except Exception as e:
                # Provide context about which statement failed in the script
                raise Exception(f"SQL script execution failed at statement {i}/{len(statements)}: {statement}\nError: {str(e)}") from e


class MigrationRunner:
    """Main migration runner class."""
    
    def __init__(self, config_path: str = "app/core/db/data_migrations/data_migration_config.ini"):
        """Initialize migration runner.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.commands = MigrationCommands(self.config)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file.
        
        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        config = configparser.ConfigParser(interpolation=None)
        config.read(self.config_path)
        
        # Convert to dictionary
        config_dict = {}
        for section in config.sections():
            config_dict.update(dict(config.items(section)))
        
        return config_dict
    
    def _get_connection(self) -> AsyncConnection:
        """Get database connection.
        
        Returns:
            AsyncConnection: Database connection
        """
        # Use database URL from environment variables via settings
        database_url = settings.postgres_database_url
        engine = create_async_engine(database_url)
        return engine.connect()
    
    async def create_migration(self, message: str) -> None:
        """Create a new migration.
        
        Args:
            message: Migration description
        """
        revision_id = await self.commands.create_migration(message)
        print(f"Created migration with revision ID: {revision_id}")
    
    async def upgrade(self, target_revision: Optional[str] = None) -> None:
        """Upgrade database.
        
        Args:
            target_revision: Target revision (latest if None)
        """
        try:
            async with self._get_connection() as connection:
                await self.commands.upgrade(connection, target_revision)
                print("✓ Database upgrade completed successfully")
        except Exception as e:
            print(f"✗ Database upgrade failed: {str(e)}")
            raise
    
    async def downgrade(self, target_revision: str) -> None:
        """Downgrade database.
        
        Args:
            target_revision: Target revision to downgrade to
        """
        try:
            async with self._get_connection() as connection:
                await self.commands.downgrade(connection, target_revision)
                print("✓ Database downgrade completed successfully")
        except Exception as e:
            print(f"✗ Database downgrade failed: {str(e)}")
            raise
    
    async def current(self) -> None:
        """Show current migration head."""
        async with self._get_connection() as connection:
            current_head = await self.commands.current(connection)
            if current_head:
                print(f"Current head: {current_head}")
            else:
                print("No migrations have been applied")
    
    async def history(self) -> None:
        """Show migration history."""
        async with self._get_connection() as connection:
            history = await self.commands.history(connection)
            
            if not history:
                print("No migrations found")
                return
            
            print("Migration History:")
            print("-" * 80)
            for migration in history:
                status = "✓" if migration['applied'] else "✗"
                print(f"{status} {migration['revision']} - {migration['description']}")
    
    def run_cli(self) -> None:
        """Run the command-line interface."""
        parser = argparse.ArgumentParser(description="Custom Migration System")
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Create migration command
        create_parser = subparsers.add_parser('create', help='Create a new migration')
        create_parser.add_argument('message', help='Migration description')
        
        # Upgrade command
        upgrade_parser = subparsers.add_parser('upgrade', help='Upgrade database')
        upgrade_parser.add_argument('--target', help='Target revision')
        
        # Downgrade command
        downgrade_parser = subparsers.add_parser('downgrade', help='Downgrade database')
        downgrade_parser.add_argument('target', help='Target revision')
        
        # Current command
        subparsers.add_parser('current', help='Show current head')
        
        # History command
        subparsers.add_parser('history', help='Show migration history')
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        # Run the appropriate command
        if args.command == 'create':
            asyncio.run(self.create_migration(args.message))
        elif args.command == 'upgrade':
            asyncio.run(self.upgrade(args.target))
        elif args.command == 'downgrade':
            asyncio.run(self.downgrade(args.target))
        elif args.command == 'current':
            asyncio.run(self.current())
        elif args.command == 'history':
            asyncio.run(self.history())


def main():
    """Main entry point for CLI."""
    runner = MigrationRunner()
    runner.run_cli()


if __name__ == "__main__":
    main()