# In models.py or auditing.py

from sqlalchemy import String, DateTime, func, Index, Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, TYPE_CHECKING, Any
from datetime import datetime   

from sqlmodel import Field, Relationship
from app.core.models import BigIntIDModel, TimestampedModel

if TYPE_CHECKING:
    pass

class Audit(TimestampedModel, BigIntIDModel, table=True):
    __tablename__ = 'audit' # Renamed from 'activity' for clarity

    table_name: str = Field()
    target_id: str = Field() 
    verb: str = Field()
    
    # What changed
    old_data: dict[str, Any] | None = Field(sa_column=Column(JSONB, nullable=True))
    new_data: dict[str, Any] | None = Field(sa_column=Column(JSONB, nullable=True))

    # Who changed it
    app_user_id: str = Field(String(255), nullable=True) # Application user (e.g., from JWT)
    db_role: str = Field(String(255), nullable=True)          # PostgreSQL role that made the change

    # Extra context (The "How")
    request_id: str = Field(String(255), nullable=True) # To group changes from a single API call
    
    # When it changed
    issued_at: datetime = Field(default_factory=datetime.now) 
