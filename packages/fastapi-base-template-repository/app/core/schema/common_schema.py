"""Common schema for bulk upsert operations."""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


T = TypeVar("T")


class UpsertResult(BaseModel, Generic[T]):
    """Schema for returning results of bulk upsert operations."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    created_count: int = Field(description="Number of records created")
    updated_count: int = Field(description="Number of records updated")
    unchanged_count: int = Field(default=0, description="Number of records that had no changes")
    total_count: int = Field(description="Total number of records processed")
    created_items: list[T] = Field(description="List of newly created items")
    updated_items: list[T] = Field(description="List of updated items")
    unchanged_items: list[T] = Field(default_factory=list, description="List of items that had no changes")
