"""Candidate domain module — profile CRUD and enrichment."""

import logging
from typing import Any, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import CandidateProfile
from app.models.user import User
from app.schemas.candidate import CandidateCreate, CandidateUpdate

logger = logging.getLogger(__name__)


class CandidateModule:
    """Domain module for candidate profile operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_profile(
        self, user_id: int, data: CandidateCreate
    ) -> CandidateProfile:
        """Create a candidate profile for an existing user."""
        profile = CandidateProfile(
            user_id=user_id,
            full_name=data.full_name,
            phone=data.phone,
            education=data.education,
            skills=data.skills or [],
            location=data.location,
            district=data.district,
            state=data.state,
            social_category=data.social_category,
            is_rural=data.is_rural,
            resume_url=data.resume_url,
            mobility_preferences=data.mobility_preferences,
            profile_completion_score=self._compute_completion(data),
        )
        self.db.add(profile)
        await self.db.flush()
        await self.db.refresh(profile)
        logger.info("Created candidate profile for user %d", user_id)
        return profile

    async def get_profile(self, candidate_id: int) -> Optional[CandidateProfile]:
        """Fetch a candidate profile by ID."""
        result = await self.db.execute(
            select(CandidateProfile).where(CandidateProfile.id == candidate_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Optional[CandidateProfile]:
        """Fetch a candidate profile by user ID."""
        result = await self.db.execute(
            select(CandidateProfile).where(CandidateProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_profile(
        self, candidate_id: int, data: CandidateUpdate
    ) -> Optional[CandidateProfile]:
        """Update an existing candidate profile."""
        profile = await self.get_profile(candidate_id)
        if profile is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)

        # Recompute completion score
        profile.profile_completion_score = self._compute_completion_from_model(profile)
        await self.db.flush()
        await self.db.refresh(profile)
        logger.info("Updated candidate profile %d", candidate_id)
        return profile

    async def list_profiles(
        self,
        *,
        state: Optional[str] = None,
        district: Optional[str] = None,
        social_category: Optional[str] = None,
        is_rural: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[CandidateProfile]:
        """List candidate profiles with optional filters."""
        query = select(CandidateProfile)
        if state:
            query = query.where(CandidateProfile.state == state)
        if district:
            query = query.where(CandidateProfile.district == district)
        if social_category:
            query = query.where(CandidateProfile.social_category == social_category)
        if is_rural is not None:
            query = query.where(CandidateProfile.is_rural == is_rural)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_profiles(self) -> int:
        """Return total candidate count."""
        result = await self.db.execute(select(func.count(CandidateProfile.id)))
        return result.scalar() or 0

    @staticmethod
    def _compute_completion(data: CandidateCreate) -> float:
        """Compute profile completion score from create schema."""
        fields = [
            data.full_name,
            data.phone,
            data.education,
            data.skills,
            data.district,
            data.state,
            data.social_category,
            data.resume_url,
        ]
        filled = sum(1 for f in fields if f)
        return round(filled / len(fields), 2)

    @staticmethod
    def _compute_completion_from_model(profile: CandidateProfile) -> float:
        """Compute profile completion score from ORM model."""
        fields = [
            profile.full_name,
            profile.phone,
            profile.education,
            profile.skills,
            profile.district,
            profile.state,
            profile.social_category,
            profile.resume_url,
        ]
        filled = sum(1 for f in fields if f)
        return round(filled / len(fields), 2)
