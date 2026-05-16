"""Pydantic schemas for request/response validation."""

from app.schemas.common import PaginatedResponse, StatusEnum, MessageResponse
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate, Token, TokenRefresh
from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateResponse
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate, OpportunityResponse
from app.schemas.match import MatchResponse, MatchExplanation, ScoreBreakdown
from app.schemas.allocation import (
    AllocationResponse,
    AllocationRunRequest,
    AllocationOverride,
    AllocationCycleResponse,
    AllocationStats,
)

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
