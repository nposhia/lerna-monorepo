#!/usr/bin/env python3
"""Custom Migration System CLI Tool.

A command-line interface for the custom migration system.
Usage:
    python data_migrate.py create "Add users table"
    python data_migrate.py upgrade
    python data_migrate.py downgrade <revision_id>
    python data_migrate.py current
    python data_migrate.py history
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.db.data_migrations.data_migration_runner import MigrationRunner

if __name__ == "__main__":
    runner = MigrationRunner()
    runner.run_cli()