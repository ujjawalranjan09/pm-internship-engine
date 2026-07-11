"""Allocation endpoints: run allocation, get results, override."""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_session, get_current_user
from app.core.events import EVENT_ALLOCATION_COMPLETE, event_bus
from app.core.exceptions import AllocationException, NotFoundException
from app.models.allocation import Allocation, AllocationStatus
from app.models.allocation_cycle import AllocationCycle, CycleStatus
from app.models.user import User
from app.schemas.allocation import (
    AllocationCycleResponse,
    AllocationOverride,
    AllocationResponse,
    AllocationRunRequest,
    AllocationStats,
)
from app.schemas.common import PaginatedResponse
from app.services.allocation_service import AllocationService

router = APIRouter( tags=["Allocation"])


@router.post("/run", response_model=AllocationCycleResponse, status_code=status.HTTP_202_ACCEPTED)
async def run_allocation(
    payload: AllocationRunRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    """Trigger a new allocation cycle (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can run allocation",
        )

    cycle = AllocationCycle(
        name=payload.cycle_name,
        status=CycleStatus.RUNNING,
        config=payload.config,
        started_at=datetime.now(UTC),
    )
    db.add(cycle)
    await db.flush()
    await db.refresh(cycle)

    if payload.dry_run:
        cycle.status = CycleStatus.COMPLETED
        cycle.completed_at = datetime.now(UTC)
        await db.flush()
        return cycle

    try:
        allocation_service = AllocationService(db)
        result = await allocation_service.run_allocation(cycle_id=cycle.id)
        cycle.status = CycleStatus.COMPLETED
        cycle.completed_at = datetime.now(UTC)
        await db.flush()
        await event_bus.publish(EVENT_ALLOCATION_COMPLETE, result)
    except Exception as exc:
        cycle.status = CycleStatus.FAILED
        await db.flush()
        raise AllocationException(f"Allocation failed: {exc}") from exc

    await db.refresh(cycle)
    return cycle


@router.get("/cycles", response_model=list[AllocationCycleResponse])
async def list_cycles(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
) -> list[AllocationCycleResponse]:
    """List recent allocation cycles."""
    result = await db.execute(select(AllocationCycle).order_by(AllocationCycle.created_at.desc()).limit(limit))
    cycles = result.scalars().all()
    return [AllocationCycleResponse.model_validate(c) for c in cycles]


@router.get("/cycles/{cycle_id}", response_model=AllocationCycleResponse)
async def get_cycle(
    cycle_id: int,
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    """Get allocation cycle details."""
    result = await db.execute(select(AllocationCycle).where(AllocationCycle.id == cycle_id))
    cycle = result.scalar_one_or_none()
    if cycle is None:
        raise NotFoundException(f"Allocation cycle {cycle_id} not found")
    return cycle


@router.get("/cycles/{cycle_id}/results", response_model=PaginatedResponse[AllocationResponse])
async def get_cycle_results(
    cycle_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    """Get allocation results for a specific cycle."""
    result = await db.execute(
        select(Allocation).where(Allocation.allocation_cycle_id == cycle_id).order_by(Allocation.created_at.desc())
    )
    allocations = result.scalars().all()
    total = len(allocations)
    start = (page - 1) * page_size
    end = start + page_size
    page_items = allocations[start:end]

    return PaginatedResponse.create(
        items=[AllocationResponse.model_validate(a) for a in page_items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/cycles/{cycle_id}/stats", response_model=AllocationStats)
async def get_cycle_stats(
    cycle_id: int,
    db: AsyncSession = Depends(get_async_session),
) -> AllocationStats:
    """Get aggregate statistics for an allocation cycle."""
    result = await db.execute(select(Allocation).where(Allocation.allocation_cycle_id == cycle_id))
    allocations = result.scalars().all()

    total = len(allocations)
    confirmed = sum(1 for a in allocations if a.status == AllocationStatus.CONFIRMED)
    declined = sum(1 for a in allocations if a.status == AllocationStatus.DECLINED)

    candidates = set(a.candidate_id for a in allocations)
    opportunities = set(a.opportunity_id for a in allocations)

    return AllocationStats(
        cycle_id=cycle_id,
        total_allocated=total,
        total_confirmed=confirmed,
        total_declined=declined,
        unique_candidates=len(candidates),
        unique_opportunities=len(opportunities),
    )


@router.post("/override", response_model=AllocationResponse)
async def override_allocation(
    payload: AllocationOverride,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    """Manually override an allocation (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can override allocations",
        )

    result = await db.execute(select(Allocation).where(Allocation.id == payload.allocation_id))
    allocation = result.scalar_one_or_none()
    if allocation is None:
        raise NotFoundException(f"Allocation {payload.allocation_id} not found")

    if payload.new_opportunity_id is not None:
        allocation.opportunity_id = payload.new_opportunity_id
    if payload.new_status is not None:
        allocation.status = AllocationStatus(payload.new_status)
    allocation.explanation = f"Admin override: {payload.reason}"

    await db.flush()
    await db.refresh(allocation)
    return allocation
