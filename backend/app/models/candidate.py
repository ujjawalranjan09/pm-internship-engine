"""SQLAlchemy ORM model for internship candidates."""

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # Personal
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(50), nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)  # SC/ST/OBC/General
    is_pwd: Mapped[bool] = mapped_column(Boolean, default=False)

    # Location
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_rural: Mapped[bool] = mapped_column(Boolean, default=False)
    is_aspirational_district: Mapped[bool] = mapped_column(Boolean, default=False)
    pincode: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Education
    highest_qualification: Mapped[str | None] = mapped_column(String(100), nullable=True)
    institution: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cgpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    graduation_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stream: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Skills & Preferences
    skills: Mapped[list[Any]] = mapped_column(ARRAY(String), default=list)
    sector_preferences: Mapped[list[Any]] = mapped_column(ARRAY(String), default=list)
    location_preferences: Mapped[list[Any]] = mapped_column(ARRAY(String), default=list)
    languages: Mapped[list[Any]] = mapped_column(ARRAY(String), default=list)

    # Profile
    resume_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding: Mapped[list[Any] | None] = mapped_column(ARRAY(Float), nullable=True)
    profile_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
    )
    profile_completeness: Mapped[float] = mapped_column(Float, default=0.0)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    has_participated: Mapped[bool] = mapped_column(Boolean, default=False)
    participation_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


# Backward compatibility alias
CandidateProfile = Candidate
