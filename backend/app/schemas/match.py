"""Match Pydantic schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ScoreBreakdown(BaseModel):
    """Detailed breakdown of match scoring components."""

    skill_similarity: float = 0.0
    location_preference: float = 0.0
    education_fit: float = 0.0
    sector_interest: float = 0.0
    social_equity: float = 0.0
    profile_completeness: float = 0.0


class MatchExplanation(BaseModel):
    """Human-readable explanation of why a match was scored this way."""

    summary: str
    strengths: list[str] = []
    gaps: list[str] = []
    recommendations: list[str] = []


class MatchResponse(BaseModel):
    """Schema for match API responses."""

    id: int
    candidate_id: int
    opportunity_id: int
    score: float
    score_breakdown: dict[str, Any] | None = None
    explanation: str | None = None
    rank: int | None = None
    status: str = "pending"
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MatchCandidateBrief(BaseModel):
    """Brief candidate info included in match responses."""

    id: int
    full_name: str
    skills: list[str] | None = None
    state: str | None = None


class MatchOpportunityBrief(BaseModel):
    """Brief opportunity info included in match responses."""

    id: int
    title: str
    sector: str | None = None
    location: str | None = None


class MatchDetailResponse(MatchResponse):
    """Extended match response with candidate and opportunity details."""

    candidate: MatchCandidateBrief | None = None
    opportunity: MatchOpportunityBrief | None = None
