"""Pydantic schemas for request/response validation."""

from app.schemas.allocation import (
    AllocationCycleResponse,
    AllocationOverride,
    AllocationResponse,
    AllocationRunRequest,
    AllocationStats,
)
from app.schemas.candidate import CandidateCreate, CandidateResponse, CandidateUpdate
from app.schemas.common import MessageResponse, PaginatedResponse, StatusEnum
from app.schemas.match import MatchExplanation, MatchResponse, ScoreBreakdown
from app.schemas.opportunity import OpportunityCreate, OpportunityResponse, OpportunityUpdate
from app.schemas.user import Token, TokenRefresh, UserCreate, UserLogin, UserResponse, UserUpdate

__all__ = [
    "PaginatedResponse",
    "StatusEnum",
    "MessageResponse",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    "Token",
    "TokenRefresh",
    "CandidateCreate",
    "CandidateUpdate",
    "CandidateResponse",
    "OpportunityCreate",
    "OpportunityUpdate",
    "OpportunityResponse",
    "MatchResponse",
    "MatchExplanation",
    "ScoreBreakdown",
    "AllocationResponse",
    "AllocationRunRequest",
    "AllocationOverride",
    "AllocationCycleResponse",
    "AllocationStats",
]
