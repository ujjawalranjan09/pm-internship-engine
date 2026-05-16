"""Candidate profile Pydantic schemas."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class EducationSchema(BaseModel):
    """Education details nested schema."""

    degree: str
    institution: str
    year_of_passing: int
    percentage_cgpa: Optional[float] = None
    field_of_study: Optional[str] = None


class MobilityPreferencesSchema(BaseModel):
    """Mobility preferences nested schema."""

    willing_to_relocate: bool = False
    preferred_locations: list[str] = Field(default_factory=list)
    remote_work_ok: bool = True
    max_commute_km: Optional[int] = None


class CandidateCreate(BaseModel):
    """Schema for creating a candidate profile."""

    full_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    education: Optional[dict[str, Any]] = None
    skills: Optional[list[str]] = None
    location: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    social_category: Optional[str] = Field(
        None, pattern="^(general|obc|sc|st|ews)$"
    )
    is_rural: bool = False
    resume_url: Optional[str] = None
    mobility_preferences: Optional[dict[str, Any]] = None


class CandidateUpdate(BaseModel):
    """Schema for updating a candidate profile."""

    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    education: Optional[dict[str, Any]] = None
    skills: Optional[list[str]] = None
    location: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    social_category: Optional[str] = Field(
        None, pattern="^(general|obc|sc|st|ews)$"
    )
    is_rural: Optional[bool] = None
    resume_url: Optional[str] = None
    mobility_preferences: Optional[dict[str, Any]] = None


class CandidateResponse(BaseModel):
    """Schema for candidate API responses."""

    id: int
    user_id: int
    full_name: str
    phone: Optional[str] = None
    education: Optional[dict[str, Any]] = None
    skills: Optional[list[str]] = None
    location: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    social_category: Optional[str] = None
    is_rural: bool = False
    resume_url: Optional[str] = None
    profile_completion_score: float = 0.0
    mobility_preferences: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
