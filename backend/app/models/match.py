"""Match model for candidate-opportunity scoring."""

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Match(BaseModel):
    """Scored match between a candidate and an opportunity."""

    __tablename__ = "matches"

    candidate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    opportunity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    score: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    score_breakdown: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending", index=True
    )  # pending, accepted, rejected, waitlisted

    # Relationships
    candidate = relationship("CandidateProfile", back_populates="matches", foreign_keys=[candidate_id])
    opportunity = relationship("Opportunity", back_populates="matches", foreign_keys=[opportunity_id])
    allocation = relationship("Allocation", back_populates="match", uselist=False)

    def __repr__(self) -> str:
        return f"<Match(candidate={self.candidate_id}, opportunity={self.opportunity_id}, score={self.score:.3f})>"
