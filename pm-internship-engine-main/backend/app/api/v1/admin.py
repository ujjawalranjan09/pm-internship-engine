"""Admin endpoints: policy configuration, analytics, audit logs."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_session, get_current_user
from app.core.config import get_settings
from app.models.audit_log import AuditLog
from app.models.candidate import CandidateProfile
from app.models.match import Match
from app.models.opportunity import Opportunity
from app.models.user import User
from app.schemas.common import PaginatedResponse

router = APIRouter( tags=["Admin"])

settings = get_settings()


@router.get("/analytics/overview")
async def get_analytics_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    """Get system-wide analytics overview (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    candidates_count = (await db.execute(select(func.count()).select_from(CandidateProfile))).scalar() or 0
    opportunities_count = (
        await db.execute(
            select(func.count()).select_from(Opportunity).where(Opportunity.is_active == True)  # noqa: E712
        )
    ).scalar() or 0
    matches_count = (await db.execute(select(func.count()).select_from(Match))).scalar() or 0
    users_count = (await db.execute(select(func.count()).select_from(User))).scalar() or 0

    avg_score_result = await db.execute(select(func.avg(Match.score)))
    avg_score = avg_score_result.scalar() or 0.0

    state_dist = await db.execute(
        select(CandidateProfile.state, func.count())
        .where(CandidateProfile.state.isnot(None))
        .group_by(CandidateProfile.state)
        .order_by(func.count().desc())
        .limit(10)
    )
    state_distribution = {row[0]: row[1] for row in state_dist}

    category_dist = await db.execute(
        select(CandidateProfile.social_category, func.count())
        .where(CandidateProfile.social_category.isnot(None))
        .group_by(CandidateProfile.social_category)
    )
    category_distribution = {row[0]: row[1] for row in category_dist}

    return {
        "total_users": users_count,
        "total_candidates": candidates_count,
        "total_active_opportunities": opportunities_count,
        "total_matches": matches_count,
        "average_match_score": round(float(avg_score), 4),
        "state_distribution": state_distribution,
        "category_distribution": category_distribution,
    }


@router.get("/analytics/matching")
async def get_matching_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    """Get matching analytics (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    score_distribution = await db.execute(
        select(
            func.count().label("count"),
            func.avg(Match.score).label("avg_score"),
        )
    )
    stats = score_distribution.one()

    status_dist = await db.execute(select(Match.status, func.count()).group_by(Match.status))
    status_distribution = {row[0]: row[1] for row in status_dist}

    return {
        "total_matches": stats.count or 0,
        "average_score": round(float(stats.avg_score or 0), 4),
        "status_distribution": status_distribution,
    }


@router.get("/policy")
async def get_policy_config(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Get current matching and fairness policy configuration."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return {
        "matching_weights": settings.MATCH_WEIGHTS,
        "fairness": {
            "enabled": settings.FAIRNESS_ENABLED,
            "social_category_boost": settings.FAIRNESS_SOCIAL_CATEGORY_BOOST,
            "rural_boost": settings.FAIRNESS_RURAL_BOOST,
            "gender_parity_target": settings.FAIRNESS_GENDER_PARITY_TARGET,
        },
        "match_top_k": settings.MATCH_TOP_K,
        "match_min_score": settings.MATCH_MIN_SCORE,
    }


@router.get("/audit-logs")
async def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    action: str | None = None,
    entity_type: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    """Get audit logs with optional filters (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    query = select(AuditLog)
    count_query = select(func.count()).select_from(AuditLog)

    if action:
        query = query.where(AuditLog.action == action)
        count_query = count_query.where(AuditLog.action == action)
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
        count_query = count_query.where(AuditLog.entity_type == entity_type)

    total = (await db.execute(count_query)).scalar() or 0
    query = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    logs = result.scalars().all()

    return PaginatedResponse.create(
        items=[
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
        total=total,
        page=page,
        page_size=page_size,
    )
