"""Opportunity domain module — CRUD and search integration."""

import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.opportunity import Opportunity
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate

logger = logging.getLogger(__name__)


class OpportunityModule:
    """Domain module for internship opportunity operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_opportunity(self, employer_id: int, data: OpportunityCreate) -> Opportunity:
        """Create a new internship opportunity."""
        opp = Opportunity(
            employer_id=employer_id,
            title=data.title,
            description=data.description,
            sector=data.sector,
            required_skills=data.required_skills or [],
            location=data.location,
            state=data.state,
            district=data.district,
            work_mode=data.work_mode,
            capacity=data.capacity,
            stipend=data.stipend,
            duration_months=data.duration_months,
            eligibility_criteria=data.eligibility_criteria,
            is_active=True,
        )
        self.db.add(opp)
        await self.db.flush()
        await self.db.refresh(opp)
        logger.info("Created opportunity %d: %s", opp.id, opp.title)
        return opp

    async def get_opportunity(self, opp_id: int) -> Opportunity | None:
        """Fetch an opportunity by ID."""
        result = await self.db.execute(select(Opportunity).where(Opportunity.id == opp_id))
        return result.scalar_one_or_none()

    async def update_opportunity(self, opp_id: int, data: OpportunityUpdate) -> Opportunity | None:
        """Update an existing opportunity."""
        opp = await self.get_opportunity(opp_id)
        if opp is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(opp, field, value)

        await self.db.flush()
        await self.db.refresh(opp)
        logger.info("Updated opportunity %d", opp_id)
        return opp

    async def deactivate_opportunity(self, opp_id: int) -> Opportunity | None:
        """Soft-delete an opportunity by marking it inactive."""
        opp = await self.get_opportunity(opp_id)
        if opp is None:
            return None
        opp.is_active = False
        await self.db.flush()
        await self.db.refresh(opp)
        logger.info("Deactivated opportunity %d", opp_id)
        return opp

    async def list_opportunities(
        self,
        *,
        sector: str | None = None,
        state: str | None = None,
        work_mode: str | None = None,
        is_active: bool = True,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Opportunity]:
        """List opportunities with optional filters."""
        query = select(Opportunity)
        if is_active is not None:
            query = query.where(Opportunity.is_active == is_active)
        if sector:
            query = query.where(Opportunity.sector == sector)
        if state:
            query = query.where(Opportunity.state == state)
        if work_mode:
            query = query.where(Opportunity.work_mode == work_mode)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_opportunities(self, *, is_active: bool = True) -> int:
        """Return total opportunity count."""
        query = select(func.count(Opportunity.id))
        if is_active is not None:
            query = query.where(Opportunity.is_active == is_active)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_capacity_map(self, opp_ids: list[int]) -> dict[int, int]:
        """Return remaining capacity for a list of opportunity IDs."""
        if not opp_ids:
            return {}
        result = await self.db.execute(select(Opportunity).where(Opportunity.id.in_(opp_ids)))
        opps = result.scalars().all()
        return {o.id: o.capacity for o in opps}
