"""Allocation cycle management endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import RoleChecker
from app.services.allocation_service import AllocationService

router = APIRouter(prefix="/allocation", tags=["allocation"])

admin_only = RoleChecker(["admin"])


class CycleCreateRequest(BaseModel):
    name: str
    metadata: dict[str, Any] | None = None


@router.post("/cycles", status_code=201, dependencies=[Depends(admin_only)])
async def create_cycle(
    payload: CycleCreateRequest,
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    service = AllocationService(db)
    cycle = await service.create_cycle(name=payload.name, metadata=payload.metadata)
    return {"id": cycle.id, "name": cycle.name, "status": cycle.status}


@router.post("/cycles/{cycle_id}/run", dependencies=[Depends(admin_only)])
async def run_cycle(
    cycle_id: int,
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    service = AllocationService(db)
    try:
        summary = await service.run_cycle(cycle_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return summary


@router.get("/cycles/{cycle_id}", dependencies=[Depends(admin_only)])
async def get_cycle(
    cycle_id: int,
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    service = AllocationService(db)
    try:
        return await service.get_cycle_summary(cycle_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/matches/{match_id}/confirm", dependencies=[Depends(admin_only)])
async def confirm_match(
    match_id: int,
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    service = AllocationService(db)
    try:
        match = await service.confirm_match(match_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"match_id": match.id, "status": match.status}
