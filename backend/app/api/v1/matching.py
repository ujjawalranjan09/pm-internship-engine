"""Matching endpoints: trigger matching and retrieve results."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import RoleChecker, get_current_user
from app.models.candidate import Candidate
from app.models.match import Match
from app.models.user import User

router = APIRouter(prefix="/matching", tags=["matching"])

admin_only = RoleChecker(["admin"])


class MatchTriggerRequest(BaseModel):
    cycle_id: int | None = None
    top_k: int = 10


@router.post("/trigger", dependencies=[Depends(admin_only)])
async def trigger_matching(
    payload: MatchTriggerRequest,
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    # Placeholder: real pipeline call would go here
    return {"status": "queued", "cycle_id": payload.cycle_id, "top_k": payload.top_k}


@router.get("/my-matches")
async def get_my_matches(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
    limit: int = 10,
) -> Any:
    cand_result = await db.execute(
        select(Candidate).where(Candidate.user_id == current_user.id)
    )
    candidate = cand_result.scalar_one_or_none()
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    result = await db.execute(
        select(Match)
        .where(Match.candidate_id == candidate.id)
        .order_by(Match.total_score.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{match_id}")
async def get_match_detail(
    match_id: int,
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalar_one_or_none()
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return match
