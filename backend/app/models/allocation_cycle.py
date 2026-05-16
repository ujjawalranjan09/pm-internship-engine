"""SQLAlchemy ORM model for allocation (batch) cycles."""

from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import DateTime, Integer, JSON, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class CycleStatus(str, Enum):
    """Status values for allocation cycles."""

    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Base(DeclarativeBase):
    pass


class AllocationCycle(Base):
    __tablename__ = "allocation_cycles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft/active/completed/cancelled
    total_candidates: Mapped[int] = mapped_column(Integer, default=0)
    total_opportunities: Mapped[int] = mapped_column(Integer, default=0)
    total_matches: Mapped[int] = mapped_column(Integer, default=0)
    cycle_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
