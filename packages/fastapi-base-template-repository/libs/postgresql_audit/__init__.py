"""Audit library module."""

from libs.postgresql_audit.audit_service import (
    sync_audit_triggers,
    add_audit_trigger_for_table,
    remove_audit_trigger_for_table,
)

__all__ = [
    "sync_audit_triggers",
    "add_audit_trigger_for_table", 
    "remove_audit_trigger_for_table",
] 