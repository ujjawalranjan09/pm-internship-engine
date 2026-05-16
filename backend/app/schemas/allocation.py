"""Allocation Pydantic schemas."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class AllocationRunRequest(BaseModel):
    """Request to trigger a new allocation cycle."""

    cycle_name: str = Field(..., min_length=1, max_length=255)
    config: Optional[dict[str, Any]] = None
    dry_run: bool = False


class AllocationOverride(BaseModel):
    """Manual override of an allocation."""

    allocation_id: int
    new_opportunity_id: Optional[int] = None
    new_status: Optional[str] = None
    reason: str = Field(..., min_length=1)


class AllocationResponse(BaseModel):
    """Schema for allocation API responses."""

    id: int
    candidate_id: int
    opportunity_id: int
    match_id: Optional[int] = None
    allocation_cycle_id: int
    status: str
    explanation: Optional[str] = None
    allocated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AllocationCycleResponse(BaseModel):
    """Schema for allocation cycle API responses."""

    id: int
    name: str
    status: str
    config: Optional[dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AllocationStats(BaseModel):
    """Aggregate statistics for an allocation cycle."""

    cycle_id: int
    total_allocated: int = 0
    total_confirmed: int = 0
    total_declined: int = 0
    total_waitlisted: int = 0
    avg_match_score: float = 0.0
    unique_candidates: int = 0
    unique_opportunities: int = 0
