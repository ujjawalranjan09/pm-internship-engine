"""Identity domain module — user management and authentication."""

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.user import User

logger = logging.getLogger(__name__)


class IdentityModule:
    """Domain module for user identity operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_user(
        self,
        email: str,
        password: str,
        role: str = "candidate",
    ) -> User:
        """Register a new user with hashed password."""
        user = User(
            email=email.lower().strip(),
            password_hash=get_password_hash(password),
            role=role,
            is_active=True,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        logger.info("Created user %d (%s, role=%s)", user.id, email, role)
        return user

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Verify credentials and return the user if valid."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower().strip())
        )
        user = result.scalar_one_or_none()
        if user is None:
            return None
        if not user.is_active:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    async def get_user(self, user_id: int) -> Optional[User]:
        """Fetch a user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none()

    async def deactivate_user(self, user_id: int) -> Optional[User]:
        """Soft-delete a user by marking them inactive."""
        user = await self.get_user(user_id)
        if user is None:
            return None
        user.is_active = False
        await self.db.flush()
        await self.db.refresh(user)
        logger.info("Deactivated user %d", user_id)
        return user

    async def change_password(
        self, user_id: int, old_password: str, new_password: str
    ) -> bool:
        """Change user password after verifying the old one."""
        user = await self.get_user(user_id)
        if user is None:
            return False
        if not verify_password(old_password, user.password_hash):
            return False
        user.password_hash = get_password_hash(new_password)
        await self.db.flush()
        logger.info("Password changed for user %d", user_id)
        return True

    async def list_users(
        self,
        *,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[User]:
        """List users with optional filters."""
        query = select(User)
        if role:
            query = query.where(User.role == role)
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
