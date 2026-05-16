"""Allocation model for final candidate-opportunity assignments."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class AllocationStatus(enum.StrEnum):
    """Possible allocation statuses."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    WITHDRAWN = "withdrawn"
    COMPLETED = "completed"


class Allocation(BaseModel):
    """Final allocation of a candidate to an opportunity."""

    __tablename__ = "allocations"

    candidate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    opportunity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    match_id: Mapped[int] = mapped_column(Integer, ForeignKey("matches.id", ondelete="SET NULL"), nullable=True)
    allocation_cycle_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("allocation_cycles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[AllocationStatus] = mapped_column(
        Enum(AllocationStatus, name="allocation_status_enum"),
        nullable=False,
        default=AllocationStatus.PENDING,
        index=True,
    )
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    allocated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    candidate = relationship("CandidateProfile", back_populates="allocations", foreign_keys=[candidate_id])
    opportunity = relationship("Opportunity", back_populates="allocations", foreign_keys=[opportunity_id])
    match = relationship("Match", back_populates="allocation")
    cycle = relationship("AllocationCycle", back_populates="allocations")

    def __repr__(self) -> str:
        return (
            f"<Allocation(candidate={self.candidate_id}, opportunity={self.opportunity_id}, "
            f"status={self.status.value})>"
        )
