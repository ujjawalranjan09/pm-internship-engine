"""Admin-only endpoints: stats, audit log, and user management."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import RoleChecker
from app.models.audit_log import AuditLog
from app.models.candidate import Candidate
from app.models.match import Match
from app.models.opportunity import Opportunity
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])

admin_only = RoleChecker(["admin"])


@router.get("/stats", dependencies=[Depends(admin_only)])
async def get_stats(db: AsyncSession = Depends(get_async_session)) -> Any:
    async def _count(model: Any) -> int:
        result = await db.execute(select(func.count()).select_from(model))
        value = result.scalar()
        return int(value) if value is not None else 0

    return {
        "total_users": await _count(User),
        "total_candidates": await _count(Candidate),
        "total_opportunities": await _count(Opportunity),
        "total_matches": await _count(Match),
    }


@router.get("/audit-logs", dependencies=[Depends(admin_only)])
async def list_audit_logs(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    result = await db.execute(
        select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
    )
    return result.scalars().all()


@router.get("/users", dependencies=[Depends(admin_only)])
async def list_users(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    result = await db.execute(select(User).limit(limit).offset(offset))
    return result.scalars().all()


@router.patch("/users/{user_id}/deactivate", dependencies=[Depends(admin_only)])
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    await db.flush()
    return {"user_id": user_id, "is_active": False}
