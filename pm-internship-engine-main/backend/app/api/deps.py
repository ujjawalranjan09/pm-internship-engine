"""Shared API dependencies for dependency injection."""

from app.core.database import get_async_session
from app.core.security import RoleChecker, get_current_user

__all__ = ["get_async_session", "get_current_user", "RoleChecker"]
