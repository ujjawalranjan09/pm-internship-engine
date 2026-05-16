"""Notification service stub for email/SMS delivery."""

import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification

logger = logging.getLogger(__name__)


class NotificationService:
    """Handles sending notifications via email, SMS, and in-app channels.

    This is a stub implementation for the prototype. In production,
    integrate with actual email (SendGrid/SES) and SMS (Twilio) providers.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def send_allocation_notification(
        self,
        user_id: int,
        candidate_name: str,
        opportunity_title: str,
        status: str,
    ) -> Notification:
        """Send allocation status notification."""
        subject = f"Internship Allocation Update - {status.title()}"
        body = self._build_allocation_body(candidate_name, opportunity_title, status)
        return await self._create_and_send(user_id, "in_app", subject, body)

    async def send_match_notification(
        self,
        user_id: int,
        candidate_name: str,
        num_matches: int,
    ) -> Notification:
        """Notify candidate about new matches."""
        subject = f"{num_matches} New Internship Matches Found!"
        body = (
            f"Dear {candidate_name},\n\n"
            f"We found {num_matches} internship opportunities that match your profile. "
            f"Log in to view your recommendations and apply.\n\n"
            f"Best regards,\nPM Internship Scheme"
        )
        return await self._create_and_send(user_id, "in_app", subject, body)

    async def send_welcome_notification(self, user_id: int, name: str) -> Notification:
        """Send welcome notification to new user."""
        subject = "Welcome to PM Internship Scheme"
        body = (
            f"Dear {name},\n\n"
            f"Welcome to the PM Internship Smart Allocation Engine! "
            f"Complete your profile to get matched with the best internship opportunities.\n\n"
            f"Best regards,\nPM Internship Scheme"
        )
        return await self._create_and_send(user_id, "in_app", subject, body)

    async def _create_and_send(
        self,
        user_id: int,
        notification_type: str,
        subject: str,
        body: str,
    ) -> Notification:
        """Create notification record and attempt delivery."""
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            subject=subject,
            body=body,
            status="sent",
            sent_at=datetime.now(timezone.utc),
        )
        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)

        logger.info(
            "Notification sent: id=%d, type=%s, user=%d, subject=%s",
            notification.id,
            notification_type,
            user_id,
            subject,
        )

        # Stub: In production, call email/SMS API here
        if notification_type == "email":
            await self._send_email_stub(user_id, subject, body)
        elif notification_type == "sms":
            await self._send_sms_stub(user_id, body)

        return notification

    async def _send_email_stub(self, user_id: int, subject: str, body: str) -> None:
        """Stub for email delivery. Replace with SendGrid/SES integration."""
        logger.info("EMAIL STUB -> user=%d, subject=%s", user_id, subject)

    async def _send_sms_stub(self, user_id: int, body: str) -> None:
        """Stub for SMS delivery. Replace with Twilio integration."""
        logger.info("SMS STUB -> user=%d, body=%s", user_id, body[:50])

    def _build_allocation_body(self, candidate_name: str, opportunity_title: str, status: str) -> str:
        """Build allocation notification body."""
        status_messages = {
            "pending": f"has been provisionally allocated to '{opportunity_title}'. Please confirm or decline.",
            "confirmed": f"allocation to '{opportunity_title}' has been confirmed.",
            "accepted": f"Congratulations! You have accepted the internship at '{opportunity_title}'.",
            "declined": f"Your allocation to '{opportunity_title}' has been declined.",
            "withdrawn": f"Your allocation to '{opportunity_title}' has been withdrawn.",
            "completed": f"Your internship at '{opportunity_title}' has been marked as completed.",
        }
        message = status_messages.get(status, f"status updated to '{status}' for '{opportunity_title}'.")
        return (
            f"Dear {candidate_name},\n\n"
            f"Your internship {message}\n\n"
            f"Best regards,\nPM Internship Scheme"
        )
