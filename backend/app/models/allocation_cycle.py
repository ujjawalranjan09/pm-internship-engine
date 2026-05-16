"""Allocation cycle model for batch allocation runs."""

import enum
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class CycleStatus(enum.StrEnum):
    """Possible allocation cycle statuses."""

    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AllocationCycle(BaseModel):
    """A batch allocation run with its configuration."""

    __tablename__ = "allocation_cycles"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[CycleStatus] = mapped_column(
        Enum(CycleStatus, name="cycle_status_enum"),
        nullable=False,
        default=CycleStatus.DRAFT,
        index=True,
    )
    config: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    allocations = relationship("Allocation", back_populates="cycle")
    waitlist_entries = relationship("WaitlistEntry", back_populates="cycle")

    def __repr__(self) -> str:
        return f"<AllocationCycle(id={self.id}, name={self.name!r}, status={self.status.value})>"
