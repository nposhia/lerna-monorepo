"""Migration commands for creating, upgrading, and downgrading database schema.

This module provides the core migration functionality similar to Alembic commands.
"""

import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from string import Template
from typing import List, Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncConnection

from .data_migration_table import MigrationTable
from .data_migration_template import get_template
import uuid

class MigrationCommands:
    """Handles migration commands like create, upgrade, downgrade."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize migration commands.
        
        Args:
            config: Migration configuration dictionary
        """
        self.config = config
        
        # Allow environment variable override for migration table name
        migration_table_name = os.getenv(
            'MIGRATION_TABLE_NAME',
            config.get('migration_table_name', 'custom_migration_version')
        )
        
        self.migration_table = MigrationTable(migration_table_name)
        self.script_location = config.get('script_location', 'app/core/db/data_migrations')
        self.version_locations = config.get('version_locations', 'app/core/db/data_migrations/versions')
    
    def _generate_revision_id(self) -> str:
        """Generate a unique revision ID.
        
        Returns:
            str: Unique revision ID
        """
        return str(uuid.uuid4())
    
    def _get_migration_files(self) -> List[Dict[str, Any]]:
        """Get all migration files from the versions directory.
        
        Returns:
            List[Dict[str, Any]]: List of migration file info
        """
        versions_path = Path(self.version_locations)
        if not versions_path.exists():
            return []
        
        migrations = []
        for file_path in versions_path.glob("*.py"):
            if file_path.name == "__init__.py":
                continue
                
            # Extract revision from file content instead of filename
            migration_info = self._get_migration_info(file_path)
            if migration_info.get('revision'):
                migrations.append({
                    'revision': migration_info['revision'],
                    'file_path': file_path,
                    'filename': file_path.name
                })
        
        return sorted(migrations, key=lambda x: x['filename'])
    
    def _get_migration_info(self, file_path: Path) -> Dict[str, Any]:
        """Extract migration info from a migration file.
        
        Args:
            file_path: Path to migration file
            
        Returns:
            Dict[str, Any]: Migration information
        """
        with open(file_path, 'r') as f:
            content = f.read()
        
        info = {}
        
        # Extract revision
        revision_match = re.search(r'revision:\s*str\s*=\s*[\'"]([^\'"]+)[\'"]', content)
        if revision_match:
            info['revision'] = revision_match.group(1)
        
        # Extract down_revision
        down_revision_match = re.search(r'down_revision:\s*Union\[str,\s*None\]\s*=\s*(?:[\'"]([^\'"]*)[\'"]|None)', content)
        if down_revision_match:
            down_rev = down_revision_match.group(1)
            info['down_revision'] = down_rev if down_rev else None
        
        # Extract description from docstring
        desc_match = re.search(r'"""([^"]+)"""', content)
        if desc_match:
            info['description'] = desc_match.group(1).strip()
        
        return info
    
    async def create_migration(
        self, 
        message: str, 
        auto_generate: bool = False
    ) -> str:
        """Create a new migration file.
        
        Args:
            message: Migration description
            auto_generate: Whether to auto-generate migration content
            
        Returns:
            str: Created migration revision ID
        """
        # Generate revision ID
        revision_id = self._generate_revision_id()
        
        # Get current head
        migrations = self._get_migration_files()
        down_revision = None
        if migrations:
            last_migration = migrations[-1]
            down_revision = last_migration['revision']
        # Create timestamp
        now = datetime.utcnow()
        timestamp = now.strftime("%Y_%m_%d_%H%M")
        
        # Create filename
        slug = re.sub(r'[^\w\s-]', '', message.lower())
        slug = re.sub(r'[-\s]+', '_', slug)[:40]
        filename = f"{timestamp}_{revision_id}_{slug}.py"
        
        # Create versions directory if it doesn't exist
        versions_path = Path(self.version_locations)
        versions_path.mkdir(parents=True, exist_ok=True)
        
        # Generate migration content
        template = Template(get_template())
        content = template.substitute(
            message=message,
            up_revision=revision_id,
            down_revision=down_revision or "None",
            down_revision_quoted=f'"{down_revision}"' if down_revision else "None",
            branch_labels=None,
            branch_labels_quoted="None",
            depends_on=None,
            depends_on_quoted="None",
            create_date=now.strftime("%Y-%m-%d %H:%M:%S.%f")
        )
        
        # Write migration file
        file_path = versions_path / filename
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Generated migration: {filename}")
        return revision_id
    
    async def upgrade(
        self, 
        connection: AsyncConnection, 
        target_revision: Optional[str] = None
    ) -> None:
        """Upgrade database to target revision.
        
        Args:
            connection: Database connection
            target_revision: Target revision (latest if None)
        """
        # Ensure migration table exists
        if not await self.migration_table.table_exists(connection):
            await self.migration_table.create_table(connection)
        
        # Get applied and available migrations
        applied_migrations = await self.migration_table.get_applied_migrations(connection)
        available_migrations = self._get_migration_files()
        
        # Find migrations to apply
        migrations_to_apply = []
        for migration in available_migrations:
            if migration['revision'] not in applied_migrations:
                migrations_to_apply.append(migration)
                if target_revision and migration['revision'] == target_revision:
                    break
        
        # Apply migrations
        for migration in migrations_to_apply:
            print(f"Applying migration: {migration['filename']}")
            
            try:
                # Import and execute migration
                await self._execute_migration(connection, migration['file_path'], 'upgrade')
                
                # Mark as applied only if execution was successful
                migration_info = self._get_migration_info(migration['file_path'])
                await self.migration_table.mark_migration_applied(
                    connection, 
                    migration['revision'],
                    migration_info.get('description')
                )
                
                print(f"✓ Successfully applied migration: {migration['revision']}")
                
            except Exception as e:
                print(f"✗ Failed to apply migration {migration['revision']}: {str(e)}")
                # Stop processing further migrations if one fails
                raise Exception(f"Migration upgrade failed at {migration['filename']}: {str(e)}") from e
    
    async def downgrade(
        self, 
        connection: AsyncConnection, 
        target_revision: str
    ) -> None:
        """Downgrade database to target revision.
        
        Args:
            connection: Database connection
            target_revision: Target revision to downgrade to
        """
        # Get applied migrations
        applied_migrations = await self.migration_table.get_applied_migrations(connection)
        available_migrations = self._get_migration_files()

        ordered_applied = [
            m for m in available_migrations if m["revision"] in applied_migrations
        ]

        if not ordered_applied:
            print("No applied migrations found.")
            return

        # Handle `-1`: rollback only the last applied migration
        if target_revision == "-1":
            last_migration = ordered_applied[-1]
            print(f"Rolling back latest migration: {last_migration['filename']}")
            
            try:
                await self._execute_migration(connection, last_migration["file_path"], "downgrade")
                await self.migration_table.unmark_migration_applied(connection, last_migration["revision"])
                print(f"✓ Successfully rolled back migration: {last_migration['revision']}")
            except Exception as e:
                print(f"✗ Failed to rollback migration {last_migration['revision']}: {str(e)}")
                raise Exception(f"Migration downgrade failed for {last_migration['filename']}: {str(e)}") from e
            return

        # Validate that target revision is a valid available migration
        valid_revisions = [m["revision"] for m in available_migrations]
        if target_revision not in valid_revisions:
            raise ValueError(f"Invalid target revision: {target_revision}")
        
        # Find migrations to rollback
        migrations_to_rollback = []
        for migration in reversed(available_migrations):
            if migration['revision'] in applied_migrations:
                migrations_to_rollback.append(migration)
                if migration['revision'] == target_revision:
                    break
        
        # Remove the target revision from rollback list
        if migrations_to_rollback and migrations_to_rollback[-1]['revision'] == target_revision:
            migrations_to_rollback.pop()
        
        # Rollback migrations
        for migration in migrations_to_rollback:
            print(f"Rolling back migration: {migration['filename']}")
            
            try:
                # Import and execute migration
                await self._execute_migration(connection, migration['file_path'], 'downgrade')
                
                # Mark as not applied only if execution was successful
                await self.migration_table.unmark_migration_applied(
                    connection, 
                    migration['revision']
                )
                
                print(f"✓ Successfully rolled back migration: {migration['revision']}")
                
            except Exception as e:
                print(f"✗ Failed to rollback migration {migration['revision']}: {str(e)}")
                # Stop processing further migrations if one fails
                raise Exception(f"Migration downgrade failed at {migration['filename']}: {str(e)}") from e
    
    async def _execute_migration(
        self, 
        connection: AsyncConnection, 
        file_path: Path, 
        direction: str
    ) -> None:
        """Execute a migration file.
        
        Args:
            connection: Database connection
            file_path: Path to migration file
            direction: 'upgrade' or 'downgrade'
            
        Raises:
            Exception: If migration execution fails
        """
        import importlib.util
        import sys
        
        # Import migration module
        spec = importlib.util.spec_from_file_location(
            f"migration_{file_path.stem}", 
            file_path
        )
        module = importlib.util.module_from_spec(spec)
        
        # Add the module to sys.modules to avoid import issues
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        
        try:
            # Execute migration function
            if hasattr(module, direction):
                migration_func = getattr(module, direction)
                # Import MigrationContext here to avoid circular imports
                from .data_migration_runner import MigrationContext
                context = MigrationContext(connection, self.config)
                await migration_func(connection, context)
            else:
                error_msg = f"No {direction} function found in {file_path}"
                print(f"Error: {error_msg}")
                raise ValueError(error_msg)
        except Exception as e:
            # Clean up the module from sys.modules in case of error
            if spec.name in sys.modules:
                del sys.modules[spec.name]
            # Re-raise the exception with more context
            raise Exception(f"Migration {direction} failed in {file_path.name}: {str(e)}") from e
        
        # Clean up the module from sys.modules
        if spec.name in sys.modules:
            del sys.modules[spec.name]
    
    async def current(self, connection: AsyncConnection) -> Optional[str]:
        """Get current migration head.
        
        Args:
            connection: Database connection
            
        Returns:
            Optional[str]: Current head revision
        """
        return await self.migration_table.get_current_head(connection)
    
    async def history(self, connection: AsyncConnection) -> List[Dict[str, Any]]:
        """Get migration history.
        
        Args:
            connection: Database connection
            
        Returns:
            List[Dict[str, Any]]: Migration history
        """
        applied_migrations = await self.migration_table.get_applied_migrations(connection)
        available_migrations = self._get_migration_files()
        
        history = []
        for migration in available_migrations:
            migration_info = self._get_migration_info(migration['file_path'])
            history.append({
                'revision': migration['revision'],
                'description': migration_info.get('description', ''),
                'applied': migration['revision'] in applied_migrations,
                'filename': migration['filename']
            })
        
        return history