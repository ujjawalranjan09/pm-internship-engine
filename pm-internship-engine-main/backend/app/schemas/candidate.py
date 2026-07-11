"""Candidate profile Pydantic schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EducationSchema(BaseModel):
    """Education details nested schema."""

    degree: str
    institution: str
    year_of_passing: int
    percentage_cgpa: float | None = None
    field_of_study: str | None = None


class MobilityPreferencesSchema(BaseModel):
    """Mobility preferences nested schema."""

    willing_to_relocate: bool = False
    preferred_locations: list[str] = Field(default_factory=list)
    remote_work_ok: bool = True
    max_commute_km: int | None = None


class CandidateCreate(BaseModel):
    """Schema for creating a candidate profile."""

    full_name: str = Field(..., min_length=1, max_length=255)
    phone: str | None = Field(None, max_length=20)
    education: dict[str, Any] | None = None
    skills: list[str] | None = None
    location: str | None = None
    district: str | None = None
    state: str | None = None
    social_category: str | None = Field(None, pattern="^(general|obc|sc|st|ews)$")
    is_rural: bool = False
    resume_url: str | None = None
    mobility_preferences: dict[str, Any] | None = None


class CandidateUpdate(BaseModel):
    """Schema for updating a candidate profile."""

    full_name: str | None = Field(None, min_length=1, max_length=255)
    phone: str | None = Field(None, max_length=20)
    education: dict[str, Any] | None = None
    skills: list[str] | None = None
    location: str | None = None
    district: str | None = None
    state: str | None = None
    social_category: str | None = Field(None, pattern="^(general|obc|sc|st|ews)$")
    is_rural: bool | None = None
    resume_url: str | None = None
    mobility_preferences: dict[str, Any] | None = None


class CandidateResponse(BaseModel):
    """Schema for candidate API responses."""

    id: int
    user_id: int
    full_name: str
    phone: str | None = None
    education: dict[str, Any] | None = None
    skills: list[str] | None = None
    location: str | None = None
    district: str | None = None
    state: str | None = None
    social_category: str | None = None
    is_rural: bool = False
    resume_url: str | None = None
    profile_completion_score: float = 0.0
    mobility_preferences: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
