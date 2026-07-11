"""Audit domain module — immutable audit trail management."""

import logging
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


class AuditModule:
    """Domain module for audit trail operations.

    Audit logs are append-only and should never be modified or deleted.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def log(
        self,
        action: str,
        entity_type: str,
        entity_id: int | None = None,
        *,
        user_id: int | None = None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        """Append an audit log entry."""
        entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address,
        )
        self.db.add(entry)
        await self.db.flush()
        await self.db.refresh(entry)
        logger.debug(
            "Audit: %s %s:%s by user=%s",
            action,
            entity_type,
            entity_id,
            user_id,
        )
        return entry

    async def get_entity_history(
        self,
        entity_type: str,
        entity_id: int,
        limit: int = 100,
    ) -> list[AuditLog]:
        """Get full audit history for a specific entity."""
        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.entity_type == entity_type)
            .where(AuditLog.entity_id == entity_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_user_actions(
        self,
        user_id: int,
        *,
        action: str | None = None,
        limit: int = 100,
    ) -> list[AuditLog]:
        """Get all audit entries for a specific user."""
        query = select(AuditLog).where(AuditLog.user_id == user_id).order_by(AuditLog.created_at.desc())
        if action:
            query = query.where(AuditLog.action == action)
        query = query.limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_recent_actions(
        self,
        *,
        action: str | None = None,
        entity_type: str | None = None,
        limit: int = 100,
    ) -> list[AuditLog]:
        """Get recent audit entries with optional filters."""
        query = select(AuditLog).order_by(AuditLog.created_at.desc())
        if action:
            query = query.where(AuditLog.action == action)
        if entity_type:
            query = query.where(AuditLog.entity_type == entity_type)
        query = query.limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_actions(
        self,
        *,
        action: str | None = None,
        entity_type: str | None = None,
    ) -> int:
        """Count audit entries matching filters."""
        query = select(func.count(AuditLog.id))
        if action:
            query = query.where(AuditLog.action == action)
        if entity_type:
            query = query.where(AuditLog.entity_type == entity_type)
        result = await self.db.execute(query)
        return result.scalar() or 0
