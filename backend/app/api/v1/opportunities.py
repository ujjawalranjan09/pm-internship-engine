"""Opportunity CRUD and search endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import RoleChecker
from app.models.opportunity import Opportunity

router = APIRouter(prefix="/opportunities", tags=["opportunities"])

admin_only = RoleChecker(["admin"])


class OpportunityCreate(BaseModel):
    title: str
    company_name: str
    sector: str | None = None
    description: str | None = None
    location: str | None = None
    state: str | None = None
    required_skills: list[str] = []
    required_qualifications: list[str] = []
    total_seats: int = 1
    duration_weeks: int | None = None


@router.get("/")
async def list_opportunities(
    sector: str | None = Query(None),
    state: str | None = Query(None),
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    stmt = select(Opportunity).where(Opportunity.is_active == True)  # noqa: E712
    if sector:
        stmt = stmt.where(Opportunity.sector == sector)
    if state:
        stmt = stmt.where(Opportunity.state == state)
    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{opportunity_id}")
async def get_opportunity(
    opportunity_id: int,
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    result = await db.execute(
        select(Opportunity).where(Opportunity.id == opportunity_id)
    )
    opp = result.scalar_one_or_none()
    if opp is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opp


@router.post("/", status_code=201, dependencies=[Depends(admin_only)])
async def create_opportunity(
    payload: OpportunityCreate,
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    opp = Opportunity(**payload.model_dump())
    db.add(opp)
    await db.flush()
    return opp


@router.delete("/{opportunity_id}", dependencies=[Depends(admin_only)])
async def delete_opportunity(
    opportunity_id: int,
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    result = await db.execute(
        select(Opportunity).where(Opportunity.id == opportunity_id)
    )
    opp = result.scalar_one_or_none()
    if opp is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    opp.is_active = False
    await db.flush()
    return {"detail": "Deactivated"}
