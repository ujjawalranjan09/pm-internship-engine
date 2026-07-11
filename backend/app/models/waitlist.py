"""Waitlist model for candidates not immediately allocated."""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class WaitlistEntry(BaseModel):
    """A candidate on the waitlist for an opportunity."""

    __tablename__ = "waitlist_entries"

    candidate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    opportunity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    allocation_cycle_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("allocation_cycles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="waiting", index=True
    )  # waiting, promoted, expired, withdrawn

    # Relationships
    cycle = relationship("AllocationCycle", back_populates="waitlist_entries")

    def __repr__(self) -> str:
        return (
            f"<WaitlistEntry(candidate={self.candidate_id}, opportunity={self.opportunity_id}, "
            f"position={self.position})>"
        )
