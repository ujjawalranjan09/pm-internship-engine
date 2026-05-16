"""Notification endpoints: list and mark as read."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_session, get_current_user
from app.core.exceptions import NotFoundException
from app.models.notification import Notification
from app.models.user import User
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/")
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """List notifications for the authenticated user."""
    query = select(Notification).where(Notification.user_id == current_user.id)
    count_query = (
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == current_user.id)
    )

    if unread_only:
        query = query.where(Notification.status != "read")
        count_query = count_query.where(Notification.status != "read")

    total = (await db.execute(count_query)).scalar() or 0
    query = query.order_by(Notification.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    notifications = result.scalars().all()

    return PaginatedResponse.create(
        items=[
            {
                "id": n.id,
                "type": n.type,
                "subject": n.subject,
                "body": n.body,
                "status": n.status,
                "sent_at": n.sent_at.isoformat() if n.sent_at else None,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in notifications
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Mark a single notification as read."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    notification = result.scalar_one_or_none()
    if notification is None:
        raise NotFoundException(f"Notification {notification_id} not found")
    notification.status = "read"
    await db.flush()
    return {"message": "Notification marked as read"}


@router.put("/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Mark all notifications as read for the authenticated user."""
    await db.execute(
        update(Notification)
        .where(Notification.user_id == current_user.id, Notification.status != "read")
        .values(status="read")
    )
    await db.flush()
    return {"message": "All notifications marked as read"}
