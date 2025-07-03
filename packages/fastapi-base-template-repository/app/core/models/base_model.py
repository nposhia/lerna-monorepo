"""Base model definitions for SQLModel classes.

This module provides base model classes with common functionality like:
- Automatic table naming (converts class names to lowercase table names, overridable with __tablename__)
- UUID primary keys
- BigInt primary keys
- Created/updated timestamps
"""

from datetime import UTC, datetime
from typing import Any, ClassVar
from uuid import UUID, uuid4

from sqlalchemy import Integer, func  # pylint: disable=E1102
from sqlmodel import BigInteger, Field, SQLModel as _SQLModel


class SQLModel(_SQLModel):
    """Base model for all the models.

    Attributes:
        __tablename__ {str} -- The name of the table.
    """

    model_config: ClassVar[dict[str, Any]] = {  # type: ignore[assignment]
        "arbitrary_types_allowed": True,
    }


class IDModel(SQLModel):
    """Adds UUID primary key.

    This mixin provides a universally unique identifier (UUID) as the primary key
    for database tables. Using UUIDs provides several advantages:
    - Globally unique without coordination
    - No sequential exposure of record counts
    - Suitable for distributed systems with multiple database instances
    """

    # Primary key field
    # -----------------
    # UUID v4 primary key that's automatically generated for new records
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )


class BigIntIDModel(SQLModel):
    """Adds auto-incrementing BigInt primary key."""

    id: int = Field(
        sa_type=BigInteger,
        primary_key=True,
        nullable=False,
    )


class IntIDModel(SQLModel):
    """Adds auto-incrementing Int primary key."""

    id: int = Field(
        sa_type=Integer,
        primary_key=True,
        nullable=False,
    )


class TimestampedModel(SQLModel):
    """Adds created_at and updated_at timestamps.

    This mixin adds automatic timestamp tracking to SQLModel classes.
    It ensures all database records maintain accurate creation and
    modification timestamps in UTC format.
    """

    # Timestamp tracking fields
    # -------------------------------
    # These fields automatically track when records are created and updated
    # Both server-side (PostgreSQL) and client-side (Python) defaults are provided

    # pylint: disable=not-callable
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC).replace(tzinfo=None),
        sa_column_kwargs={"server_default": func.timezone("UTC", func.now())},
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC).replace(tzinfo=None),
        sa_column_kwargs={
            "onupdate": func.timezone("UTC", func.now()),
            "server_default": func.timezone("UTC", func.now()),
        },
        nullable=False,
    )
