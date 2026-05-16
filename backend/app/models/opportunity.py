"""SQLAlchemy ORM model for internship opportunities."""

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sector: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Location
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False)

    # Requirements
    required_skills: Mapped[list[Any]] = mapped_column(ARRAY(String), default=list)
    required_qualifications: Mapped[list[Any]] = mapped_column(ARRAY(String), default=list)
    preferred_streams: Mapped[list[Any]] = mapped_column(ARRAY(String), default=list)
    min_cgpa: Mapped[float | None] = mapped_column(Integer, nullable=True)

    # Capacity
    total_seats: Mapped[int] = mapped_column(Integer, default=1)
    filled_seats: Mapped[int] = mapped_column(Integer, default=0)
    reserved_rural: Mapped[int] = mapped_column(Integer, default=0)
    reserved_sc_st: Mapped[int] = mapped_column(Integer, default=0)

    # Timing
    application_deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    internship_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_weeks: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Metadata
    embedding: Mapped[list[Any] | None] = mapped_column(ARRAY(Integer), nullable=True)
    opportunity_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
