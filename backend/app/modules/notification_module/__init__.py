"""Notification domain module — multi-channel notification management."""

import logging
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class NotificationModule:
    """Domain module for user notification management."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._service = NotificationService(db)

    async def send_allocation_notice(
        self,
        user_id: int,
        candidate_name: str,
        opportunity_title: str,
        status: str,
    ) -> Notification:
        """Send an allocation status notification."""
        return await self._service.send_allocation_notification(
            user_id, candidate_name, opportunity_title, status
        )

    async def send_match_notice(
        self,
        user_id: int,
        candidate_name: str,
        num_matches: int,
    ) -> Notification:
        """Notify candidate about new matches."""
        return await self._service.send_match_notification(
            user_id, candidate_name, num_matches
        )

    async def send_welcome(self, user_id: int, name: str) -> Notification:
        """Send welcome notification to a new user."""
        return await self._service.send_welcome_notification(user_id, name)

    async def get_user_notifications(
        self,
        user_id: int,
        *,
        notification_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> list[Notification]:
        """Get notifications for a user with optional filters."""
        query = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
        )
        if notification_type:
            query = query.where(Notification.type == notification_type)
        if status:
            query = query.where(Notification.status == status)
        query = query.limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def mark_read(self, notification_id: int) -> Optional[Notification]:
        """Mark a notification as read."""
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        if notification is None:
            return None
        notification.status = "read"
        await self.db.flush()
        await self.db.refresh(notification)
        return notification

    async def get_unread_count(self, user_id: int) -> int:
        """Count unread notifications for a user."""
        result = await self.db.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.status.in_(["sent", "pending"]),
            )
        )
        return result.scalar() or 0
