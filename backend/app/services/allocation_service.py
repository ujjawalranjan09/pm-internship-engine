"""Orchestrates the end-to-end allocation cycle."""

import logging
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.allocation_cycle import AllocationCycle
from app.models.candidate import Candidate
from app.models.match import Match
from app.models.opportunity import Opportunity

logger = logging.getLogger(__name__)


class AllocationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_cycle(self, name: str, metadata: dict[str, Any] | None = None) -> AllocationCycle:
        cycle = AllocationCycle(name=name, cycle_metadata=metadata)
        self.db.add(cycle)
        await self.db.flush()
        logger.info("Created allocation cycle id=%s name=%s", cycle.id, name)
        return cycle

    async def run_cycle(self, cycle_id: int) -> dict[str, Any]:
        """Execute matching + allocation for a cycle and return a summary."""
        cycle_result = await self.db.execute(
            select(AllocationCycle).where(AllocationCycle.id == cycle_id)
        )
        cycle = cycle_result.scalar_one_or_none()
        if cycle is None:
            raise ValueError(f"Cycle {cycle_id} not found")

        candidate_result = await self.db.execute(
            select(Candidate).where(Candidate.is_active == True)  # noqa: E712
        )
        candidates: list[Candidate] = list(candidate_result.scalars().all())

        opp_result = await self.db.execute(
            select(Opportunity).where(Opportunity.is_active == True)  # noqa: E712
        )
        opportunities: list[Opportunity] = list(opp_result.scalars().all())

        cycle.status = "active"
        cycle.total_candidates = len(candidates)
        cycle.total_opportunities = len(opportunities)
        await self.db.flush()

        # Placeholder: real matching pipeline would be called here
        total_matches = 0

        cycle.status = "completed"
        cycle.total_matches = total_matches
        await self.db.flush()

        return {
            "cycle_id": cycle_id,
            "status": "completed",
            "candidates_processed": len(candidates),
            "opportunities_processed": len(opportunities),
            "matches_created": total_matches,
        }

    async def get_cycle_summary(self, cycle_id: int) -> dict[str, Any]:
        result = await self.db.execute(
            select(AllocationCycle).where(AllocationCycle.id == cycle_id)
        )
        cycle = result.scalar_one_or_none()
        if cycle is None:
            raise ValueError(f"Cycle {cycle_id} not found")
        return {
            "id": cycle.id,
            "name": cycle.name,
            "status": cycle.status,
            "total_candidates": cycle.total_candidates,
            "total_opportunities": cycle.total_opportunities,
            "total_matches": cycle.total_matches,
        }

    async def list_matches_for_candidate(
        self, candidate_id: int, limit: int = 20
    ) -> list[Match]:
        result = await self.db.execute(
            select(Match)
            .where(Match.candidate_id == candidate_id)
            .order_by(Match.total_score.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def confirm_match(self, match_id: int) -> Match:
        result = await self.db.execute(select(Match).where(Match.id == match_id))
        match = result.scalar_one_or_none()
        if match is None:
            raise ValueError(f"Match {match_id} not found")
        match.status = "confirmed"
        await self.db.flush()
        return match
