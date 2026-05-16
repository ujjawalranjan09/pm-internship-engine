"""Shared API dependencies for dependency injection."""

from app.core.database import get_async_session
from app.core.security import get_current_user, RoleChecker

__all__ = ["get_async_session", "get_current_user", "RoleChecker"]
