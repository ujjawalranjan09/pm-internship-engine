"""Analytics domain module — aggregate reporting and dashboards."""

import logging
from typing import Any, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.allocation import Allocation, AllocationStatus
from app.models.allocation_cycle import AllocationCycle, CycleStatus
from app.models.candidate import CandidateProfile
from app.models.match import Match
from app.models.opportunity import Opportunity
from app.models.user import User

logger = logging.getLogger(__name__)


class AnalyticsModule:
    """Domain module for system-wide analytics and reporting."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def dashboard_summary(self) -> dict[str, Any]:
        """Return high-level system metrics for the admin dashboard."""
        users = await self._count(User)
        candidates = await self._count(CandidateProfile)
        opportunities = await self._count(Opportunity, is_active=True)
        total_opps = await self._count(Opportunity)
        matches = await self._count(Match)
        allocations = await self._count(Allocation)
        cycles = await self._count(AllocationCycle)

        return {
            "total_users": users,
            "total_candidates": candidates,
            "active_opportunities": opportunities,
            "total_opportunities": total_opps,
            "total_matches": matches,
            "total_allocations": allocations,
            "total_cycles": cycles,
        }

    async def allocation_funnel(self, cycle_id: Optional[int] = None) -> dict[str, Any]:
        """Return the allocation funnel: candidates → matched → allocated → confirmed."""
        # Total candidates
        total_candidates = await self._count(CandidateProfile)

        # Matched candidates (unique)
        match_query = select(func.count(func.distinct(Match.candidate_id)))
        if cycle_id:
            # Matches created around cycle time — use all matches for now
            pass
        matched_result = await self.db.execute(match_query)
        matched = matched_result.scalar() or 0

        # Allocated
        alloc_query = select(func.count(Allocation.id))
        if cycle_id:
            alloc_query = alloc_query.where(Allocation.allocation_cycle_id == cycle_id)
        alloc_result = await self.db.execute(alloc_query)
        allocated = alloc_result.scalar() or 0

        # Confirmed
        confirm_query = select(func.count(Allocation.id)).where(
            Allocation.status == AllocationStatus.CONFIRMED
        )
        if cycle_id:
            confirm_query = confirm_query.where(Allocation.allocation_cycle_id == cycle_id)
        confirm_result = await self.db.execute(confirm_query)
        confirmed = confirm_result.scalar() or 0

        return {
            "total_candidates": total_candidates,
            "matched": matched,
            "allocated": allocated,
            "confirmed": confirmed,
            "match_rate": round(matched / total_candidates, 3) if total_candidates else 0.0,
            "allocation_rate": round(allocated / matched, 3) if matched else 0.0,
            "confirmation_rate": round(confirmed / allocated, 3) if allocated else 0.0,
        }

    async def opportunity_stats(self) -> list[dict[str, Any]]:
        """Return per-opportunity allocation counts."""
        result = await self.db.execute(
            select(
                Opportunity.id,
                Opportunity.title,
                Opportunity.sector,
                Opportunity.capacity,
                func.count(Allocation.id).label("allocated"),
            )
            .outerjoin(
                Allocation,
                Allocation.opportunity_id == Opportunity.id,
            )
            .group_by(Opportunity.id)
            .order_by(func.count(Allocation.id).desc())
        )
        return [
            {
                "opportunity_id": row.id,
                "title": row.title,
                "sector": row.sector,
                "capacity": row.capacity,
                "allocated": row.allocated,
                "fill_rate": round(row.allocated / row.capacity, 2) if row.capacity else 0.0,
            }
            for row in result.all()
        ]

    async def sector_distribution(self) -> dict[str, int]:
        """Return allocation count by sector."""
        result = await self.db.execute(
            select(Opportunity.sector, func.count(Allocation.id))
            .outerjoin(Allocation, Allocation.opportunity_id == Opportunity.id)
            .group_by(Opportunity.sector)
        )
        return {row[0] or "unknown": row[1] for row in result.all()}

    async def cycle_comparison(self) -> list[dict[str, Any]]:
        """Compare metrics across all completed cycles."""
        result = await self.db.execute(
            select(AllocationCycle).where(
                AllocationCycle.status == CycleStatus.COMPLETED
            )
        )
        cycles = result.scalars().all()

        comparisons = []
        for cycle in cycles:
            stats_result = await self.db.execute(
                select(
                    func.count(Allocation.id).label("total"),
                    func.count()
                    .filter(Allocation.status == AllocationStatus.CONFIRMED)
                    .label("confirmed"),
                ).where(Allocation.allocation_cycle_id == cycle.id)
            )
            row = stats_result.one()
            comparisons.append({
                "cycle_id": cycle.id,
                "name": cycle.name,
                "total_allocated": row.total or 0,
                "total_confirmed": row.confirmed or 0,
                "started_at": cycle.started_at.isoformat() if cycle.started_at else None,
                "completed_at": cycle.completed_at.isoformat() if cycle.completed_at else None,
            })

        return comparisons

    async def _count(self, model: Any, **filters: Any) -> int:
        """Generic count query."""
        query = select(func.count(model.id))
        for attr, value in filters.items():
            query = query.where(getattr(model, attr) == value)
        result = await self.db.execute(query)
        return result.scalar() or 0
