"""Candidate profile CRUD endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import RoleChecker, get_current_user
from app.models.candidate import Candidate
from app.models.user import User

router = APIRouter(prefix="/candidates", tags=["candidates"])

admin_only = RoleChecker(["admin"])
candidate_or_admin = RoleChecker(["candidate", "admin"])


class CandidateUpdate(BaseModel):
    full_name: str | None = None
    state: str | None = None
    district: str | None = None
    is_rural: bool | None = None
    highest_qualification: str | None = None
    cgpa: float | None = None
    skills: list[str] | None = None
    sector_preferences: list[str] | None = None
    location_preferences: list[str] | None = None
    resume_text: str | None = None


@router.get("/me")
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    result = await db.execute(
        select(Candidate).where(Candidate.user_id == current_user.id)
    )
    candidate = result.scalar_one_or_none()
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    return candidate


@router.put("/me")
async def update_my_profile(
    payload: CandidateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    result = await db.execute(
        select(Candidate).where(Candidate.user_id == current_user.id)
    )
    candidate = result.scalar_one_or_none()
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(candidate, field, value)
    await db.flush()
    return candidate


@router.get("/", dependencies=[Depends(admin_only)])
async def list_candidates(
    db: AsyncSession = Depends(get_async_session),
    limit: int = 50,
    offset: int = 0,
) -> Any:
    result = await db.execute(
        select(Candidate).where(Candidate.is_active == True).limit(limit).offset(offset)  # noqa: E712
    )
    return result.scalars().all()


@router.get("/{candidate_id}", dependencies=[Depends(admin_only)])
async def get_candidate(
    candidate_id: int,
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
