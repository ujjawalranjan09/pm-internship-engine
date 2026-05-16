"""Opportunity endpoints: CRUD and search."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_session, get_current_user
from app.core.exceptions import NotFoundException
from app.models.opportunity import Opportunity
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.opportunity import OpportunityCreate, OpportunityResponse, OpportunityUpdate

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


@router.post("/", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    payload: OpportunityCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Create a new internship opportunity (employer/admin only)."""
    if current_user.role not in ("employer", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers and admins can create opportunities",
        )
    opportunity = Opportunity(
        employer_id=current_user.id,
        **payload.model_dump(),
    )
    db.add(opportunity)
    await db.flush()
    await db.refresh(opportunity)
    return opportunity


@router.get("/", response_model=PaginatedResponse[OpportunityResponse])
async def list_opportunities(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sector: str | None = None,
    state: str | None = None,
    work_mode: str | None = None,
    is_active: bool = True,
    search: str | None = None,
    db: AsyncSession = Depends(get_async_session),
):
    """List opportunities with filters and text search."""
    query = select(Opportunity)
    count_query = select(func.count()).select_from(Opportunity)

    filters = []
    if is_active is not None:
        filters.append(Opportunity.is_active == is_active)
    if sector:
        filters.append(Opportunity.sector == sector)
    if state:
        filters.append(Opportunity.state == state)
    if work_mode:
        filters.append(Opportunity.work_mode == work_mode)
    if search:
        filters.append(Opportunity.title.ilike(f"%{search}%"))

    for f in filters:
        query = query.where(f)
        count_query = count_query.where(f)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    opportunities = result.scalars().all()

    return PaginatedResponse.create(
        items=[OpportunityResponse.model_validate(o) for o in opportunities],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: int,
    db: AsyncSession = Depends(get_async_session),
):
    """Get an opportunity by ID."""
    result = await db.execute(select(Opportunity).where(Opportunity.id == opportunity_id))
    opportunity = result.scalar_one_or_none()
    if opportunity is None:
        raise NotFoundException(f"Opportunity {opportunity_id} not found")
    return opportunity


@router.put("/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: int,
    payload: OpportunityUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Update an opportunity (owner or admin only)."""
    result = await db.execute(select(Opportunity).where(Opportunity.id == opportunity_id))
    opportunity = result.scalar_one_or_none()
    if opportunity is None:
        raise NotFoundException(f"Opportunity {opportunity_id} not found")
    if opportunity.employer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this opportunity",
        )
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(opportunity, field, value)
    await db.flush()
    await db.refresh(opportunity)
    return opportunity


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_opportunity(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Soft-delete an opportunity by setting is_active=False."""
    result = await db.execute(select(Opportunity).where(Opportunity.id == opportunity_id))
    opportunity = result.scalar_one_or_none()
    if opportunity is None:
        raise NotFoundException(f"Opportunity {opportunity_id} not found")
    if opportunity.employer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to deactivate this opportunity",
        )
    opportunity.is_active = False
    await db.flush()
