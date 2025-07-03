"""Access type enum for the application."""

from app.core.enums.base_enum import BaseEnum


class AccessType(BaseEnum):
    """Access type enum."""

    ALLOW = "ALLOW"
    DENY = "DENY"
