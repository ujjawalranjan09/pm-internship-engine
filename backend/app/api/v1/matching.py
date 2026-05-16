"""Matching endpoints: get recommendations and trigger batch matching."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_session, get_current_user
from app.core.events import EVENT_MATCHING_COMPLETE, event_bus
from app.core.exceptions import MatchingException, NotFoundException
from app.models.candidate import CandidateProfile
from app.models.match import Match
from app.models.user import User
from app.schemas.match import MatchResponse
from app.services.matching_service import MatchingService

router = APIRouter(prefix="/matching", tags=["Matching"])


@router.get("/recommendations", response_model=list[MatchResponse])
async def get_my_recommendations(
    top_k: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    """Get top-K opportunity recommendations for the authenticated candidate."""
    result = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    if profile is None:
        raise NotFoundException("Candidate profile not found. Please create your profile first.")

    matching_service = MatchingService(db)
    try:
        matches = await matching_service.get_recommendations(candidate_id=profile.id, top_k=top_k)
    except Exception as exc:
        raise MatchingException(f"Failed to generate recommendations: {exc}") from exc

    return [MatchResponse.model_validate(m) for m in matches]


@router.get("/candidate/{candidate_id}", response_model=list[MatchResponse])
async def get_candidate_matches(
    candidate_id: int,
    top_k: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    """Get matches for a specific candidate."""
    result = await db.execute(
        select(Match).where(Match.candidate_id == candidate_id).order_by(Match.score.desc()).limit(top_k)
    )
    matches = result.scalars().all()
    return [MatchResponse.model_validate(m) for m in matches]


@router.get("/opportunity/{opportunity_id}", response_model=list[MatchResponse])
async def get_opportunity_matches(
    opportunity_id: int,
    top_k: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    """Get top matches for a specific opportunity."""
    result = await db.execute(
        select(Match).where(Match.opportunity_id == opportunity_id).order_by(Match.score.desc()).limit(top_k)
    )
    matches = result.scalars().all()
    return [MatchResponse.model_validate(m) for m in matches]


@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
async def trigger_matching(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    """Trigger batch matching for all active candidates and opportunities (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can trigger batch matching",
        )

    matching_service = MatchingService(db)
    try:
        result = await matching_service.run_batch_matching()
        await event_bus.publish(EVENT_MATCHING_COMPLETE, result)
        return {
            "message": "Batch matching completed",
            "total_matches": result.get("total_matches", 0),
            "candidates_processed": result.get("candidates_processed", 0),
        }
    except Exception as exc:
        raise MatchingException(f"Batch matching failed: {exc}") from exc
