"""Candidate profile model with education, skills, and preferences."""

from typing import Any

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, JSONType


class CandidateProfile(BaseModel):
    """Extended profile for internship candidates."""

    __tablename__ = "candidate_profiles"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    education: Mapped[dict[str, Any] | None] = mapped_column(JSONType, nullable=True, default=dict)
    skills: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True, default=list)
    mobility_preferences: Mapped[dict[str, Any] | None] = mapped_column(JSONType, nullable=True, default=dict)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    social_category: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    is_rural: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resume_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile_completion_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="candidate_profile")
    matches = relationship("Match", back_populates="candidate", foreign_keys="Match.candidate_id")
    allocations = relationship("Allocation", back_populates="candidate", foreign_keys="Allocation.candidate_id")

    def __repr__(self) -> str:
        return f"<CandidateProfile(id={self.id}, name={self.full_name!r})>"
