"""create audit table and functions

Revision ID: 45e150f32d72
Revises: 
Create Date: 2025-06-19 09:46:12.818567+00:00

"""
import sqlmodel
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '45e150f32d72'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# --- SQL Definitions for Auditing Infrastructure ---

# The core trigger function that logs changes to the 'audit' table.
AUDIT_TRIGGER_FUNC_SQL = """
CREATE OR REPLACE FUNCTION audit_trigger_func() RETURNS TRIGGER AS $$
DECLARE
    app_user_id_val TEXT;
    request_id_val TEXT;
    old_data jsonb;
    new_data jsonb;
BEGIN
    -- Read session-level variables set by the application.
    app_user_id_val := current_setting('audit.app_user_id', true);
    request_id_val := current_setting('audit.request_id', true);

    -- The TG_OP variable contains the operation type (INSERT, UPDATE, DELETE).
    IF (TG_OP = 'UPDATE') THEN
        old_data := to_jsonb(OLD);
        new_data := to_jsonb(NEW);
        INSERT INTO audit (table_name, target_id, verb, old_data, new_data, app_user_id, db_role, request_id, issued_at)
        VALUES (TG_TABLE_NAME, OLD.id::TEXT, 'UPDATE', old_data, new_data, app_user_id_val, session_user, request_id_val, timezone('UTC', now()));
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        old_data := to_jsonb(OLD);
        INSERT INTO audit (table_name, target_id, verb, old_data, app_user_id, db_role, request_id, issued_at)
        VALUES (TG_TABLE_NAME, OLD.id::TEXT, 'DELETE', old_data, app_user_id_val, session_user, request_id_val, timezone('UTC', now()));
        RETURN OLD;
    ELSIF (TG_OP = 'INSERT') THEN
        new_data := to_jsonb(NEW);
        INSERT INTO audit (table_name, target_id, verb, new_data, app_user_id, db_role, request_id, issued_at)
        VALUES (TG_TABLE_NAME, NEW.id::TEXT, 'INSERT', new_data, app_user_id_val, session_user, request_id_val, timezone('UTC', now()));
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
"""

# A helper function to attach the audit trigger to a given table.
SETUP_AUDIT_FOR_TABLE_FUNC_SQL = """
CREATE OR REPLACE FUNCTION setup_audit_for_table(table_name TEXT) RETURNS VOID AS $$
BEGIN
    EXECUTE format(
        'CREATE TRIGGER audit_trigger_for_%1$I ' ||
        'AFTER INSERT OR UPDATE OR DELETE ON %1$I ' ||
        'FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();',
        table_name
    );
END;
$$ LANGUAGE plpgsql;
"""

# A helper function to remove the audit trigger from a given table.
TEARDOWN_AUDIT_FOR_TABLE_FUNC_SQL = """
CREATE OR REPLACE FUNCTION teardown_audit_for_table(table_name TEXT) RETURNS VOID AS $$
BEGIN
    EXECUTE format('DROP TRIGGER IF EXISTS audit_trigger_for_%1$I ON %1$I;', table_name);
END;
$$ LANGUAGE plpgsql;
"""


def upgrade() -> None:
    # ### Part 1: Create the 'audit' table itself ###
    print("Creating audit table...")
    op.create_table('audit',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text("timezone('UTC', now())"), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text("timezone('UTC', now())"), nullable=False),
        sa.Column('table_name', sa.String(), nullable=False),
        sa.Column('target_id', sa.String(), nullable=False),
        sa.Column('verb', sa.String(), nullable=False),
        sa.Column('old_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('new_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('app_user_id', sa.String(), nullable=True),
        sa.Column('db_role', sa.String(), nullable=True),
        sa.Column('request_id', sa.String(), nullable=True),
        sa.Column('issued_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    # Note: Index creation has been removed as per your request.

    # ### Part 2: Create the auditing infrastructure (functions) ###
    print("Creating audit helper functions...")
    op.execute(AUDIT_TRIGGER_FUNC_SQL)
    op.execute(SETUP_AUDIT_FOR_TABLE_FUNC_SQL)
    op.execute(TEARDOWN_AUDIT_FOR_TABLE_FUNC_SQL)


def downgrade() -> None:
    # ### The downgrade must happen in the exact reverse order ###
    print("Downgrading: Dropping audit helper functions...")
    op.execute("DROP FUNCTION IF EXISTS setup_audit_for_table(TEXT);")
    op.execute("DROP FUNCTION IF EXISTS teardown_audit_for_table(TEXT);")
    op.execute("DROP FUNCTION IF EXISTS audit_trigger_func();")

    print("Downgrading: Dropping audit table...")
    op.drop_table('audit')