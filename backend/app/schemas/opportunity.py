"""Opportunity Pydantic schemas."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class OpportunityCreate(BaseModel):
    """Schema for creating an opportunity."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=10)
    sector: Optional[str] = None
    required_skills: Optional[list[str]] = None
    location: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    work_mode: Optional[str] = Field(None, pattern="^(remote|hybrid|onsite)$")
    capacity: int = Field(default=1, ge=1)
    stipend: Optional[float] = Field(None, ge=0)
    duration_months: Optional[int] = Field(None, ge=1)
    eligibility_criteria: Optional[dict[str, Any]] = None


class OpportunityUpdate(BaseModel):
    """Schema for updating an opportunity."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    sector: Optional[str] = None
    required_skills: Optional[list[str]] = None
    location: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    work_mode: Optional[str] = Field(None, pattern="^(remote|hybrid|onsite)$")
    capacity: Optional[int] = Field(None, ge=1)
    stipend: Optional[float] = Field(None, ge=0)
    duration_months: Optional[int] = Field(None, ge=1)
    eligibility_criteria: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None


class OpportunityResponse(BaseModel):
    """Schema for opportunity API responses."""

    id: int
    employer_id: int
    title: str
    description: str
    sector: Optional[str] = None
    required_skills: Optional[list[str]] = None
    location: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    work_mode: Optional[str] = None
    capacity: int = 1
    stipend: Optional[float] = None
    duration_months: Optional[int] = None
    eligibility_criteria: Optional[dict[str, Any]] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
