"""Notification endpoints (placeholder for push/email notifications)."""

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import RoleChecker, get_current_user
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["notifications"])

admin_only = RoleChecker(["admin"])


class NotificationOut(BaseModel):
    id: int
    message: str
    read: bool


@router.get("/")
async def list_notifications(
    current_user: User = Depends(get_current_user),
) -> Any:
    # Placeholder: would query a notifications table
    return []


@router.post("/{notification_id}/read")
async def mark_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    return {"notification_id": notification_id, "read": True}
