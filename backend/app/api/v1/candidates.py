"""Candidate profile endpoints: CRUD and profile completion."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_session, get_current_user
from app.core.events import EVENT_PROFILE_UPDATED, event_bus
from app.core.exceptions import NotFoundException, ValidationException
from app.models.candidate import CandidateProfile
from app.models.user import User
from app.schemas.candidate import CandidateCreate, CandidateResponse, CandidateUpdate
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/candidates", tags=["Candidates"])


def _compute_profile_completion(profile: CandidateProfile) -> float:
    """Compute profile completion score (0.0 to 1.0)."""
    fields = [
        profile.full_name,
        profile.phone,
        profile.education,
        profile.skills,
        profile.location,
        profile.district,
        profile.state,
        profile.social_category,
        profile.resume_url,
        profile.mobility_preferences,
    ]
    filled = sum(1 for f in fields if f)
    return round(filled / len(fields), 2)


@router.post("/", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    payload: CandidateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Create a candidate profile for the authenticated user."""
    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Candidate profile already exists",
        )
    profile = CandidateProfile(
        user_id=current_user.id,
        **payload.model_dump(),
    )
    profile.profile_completion_score = _compute_profile_completion(profile)
    db.add(profile)
    await db.flush()
    await db.refresh(profile)
    await event_bus.publish(EVENT_PROFILE_UPDATED, {"user_id": current_user.id, "action": "created"})
    return profile


@router.get("/me", response_model=CandidateResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Get the authenticated user's candidate profile."""
    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise NotFoundException("Candidate profile not found")
    return profile


@router.put("/me", response_model=CandidateResponse)
async def update_my_profile(
    payload: CandidateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Update the authenticated user's candidate profile."""
    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise NotFoundException("Candidate profile not found")
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    profile.profile_completion_score = _compute_profile_completion(profile)
    await db.flush()
    await db.refresh(profile)
    await event_bus.publish(EVENT_PROFILE_UPDATED, {"user_id": current_user.id, "action": "updated"})
    return profile


@router.get("/", response_model=PaginatedResponse[CandidateResponse])
async def list_candidates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    state: str | None = None,
    social_category: str | None = None,
    db: AsyncSession = Depends(get_async_session),
):
    """List all candidate profiles with optional filters."""
    query = select(CandidateProfile)
    count_query = select(func.count()).select_from(CandidateProfile)

    if state:
        query = query.where(CandidateProfile.state == state)
        count_query = count_query.where(CandidateProfile.state == state)
    if social_category:
        query = query.where(CandidateProfile.social_category == social_category)
        count_query = count_query.where(CandidateProfile.social_category == social_category)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    profiles = result.scalars().all()

    return PaginatedResponse.create(
        items=[CandidateResponse.model_validate(p) for p in profiles],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: int,
    db: AsyncSession = Depends(get_async_session),
):
    """Get a candidate profile by ID."""
    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.id == candidate_id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise NotFoundException(f"Candidate {candidate_id} not found")
    return profile


@router.get("/me/completion")
async def get_profile_completion(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Get profile completion details with suggestions."""
    result = await db.execute(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise NotFoundException("Candidate profile not found")

    missing = []
    if not profile.phone:
        missing.append("phone")
    if not profile.education:
        missing.append("education")
    if not profile.skills:
        missing.append("skills")
    if not profile.location:
        missing.append("location")
    if not profile.state:
        missing.append("state")
    if not profile.social_category:
        missing.append("social_category")
    if not profile.resume_url:
        missing.append("resume")
    if not profile.mobility_preferences:
        missing.append("mobility_preferences")

    return {
        "score": profile.profile_completion_score,
        "missing_fields": missing,
        "suggestion": f"Complete your {', '.join(missing[:3])} to improve your matches."
        if missing
        else "Your profile is complete!",
    }
