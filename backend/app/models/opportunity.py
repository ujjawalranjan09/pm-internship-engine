"""Opportunity model for internship positions."""

from typing import Any

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Opportunity(BaseModel):
    """Internship opportunity posted by an employer."""

    __tablename__ = "opportunities"

    employer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    sector: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    required_skills: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True, default=list)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    work_mode: Mapped[str | None] = mapped_column(String(20), nullable=True)  # remote/hybrid/onsite
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    stipend: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    eligibility_criteria: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    matches = relationship("Match", back_populates="opportunity", foreign_keys="Match.opportunity_id")
    allocations = relationship("Allocation", back_populates="opportunity", foreign_keys="Allocation.opportunity_id")

    def __repr__(self) -> str:
        return f"<Opportunity(id={self.id}, title={self.title!r})>"
