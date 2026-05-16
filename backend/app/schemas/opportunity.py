"""Opportunity Pydantic schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class OpportunityCreate(BaseModel):
    """Schema for creating an opportunity."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=10)
    sector: str | None = None
    required_skills: list[str] | None = None
    location: str | None = None
    state: str | None = None
    district: str | None = None
    work_mode: str | None = Field(None, pattern="^(remote|hybrid|onsite)$")
    capacity: int = Field(default=1, ge=1)
    stipend: float | None = Field(None, ge=0)
    duration_months: int | None = Field(None, ge=1)
    eligibility_criteria: dict[str, Any] | None = None


class OpportunityUpdate(BaseModel):
    """Schema for updating an opportunity."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, min_length=10)
    sector: str | None = None
    required_skills: list[str] | None = None
    location: str | None = None
    state: str | None = None
    district: str | None = None
    work_mode: str | None = Field(None, pattern="^(remote|hybrid|onsite)$")
    capacity: int | None = Field(None, ge=1)
    stipend: float | None = Field(None, ge=0)
    duration_months: int | None = Field(None, ge=1)
    eligibility_criteria: dict[str, Any] | None = None
    is_active: bool | None = None


class OpportunityResponse(BaseModel):
    """Schema for opportunity API responses."""

    id: int
    employer_id: int
    title: str
    description: str
    sector: str | None = None
    required_skills: list[str] | None = None
    location: str | None = None
    state: str | None = None
    district: str | None = None
    work_mode: str | None = None
    capacity: int = 1
    stipend: float | None = None
    duration_months: int | None = None
    eligibility_criteria: dict[str, Any] | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
