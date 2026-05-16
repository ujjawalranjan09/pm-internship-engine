"""Fairness domain module — metrics, policy, and audit."""

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.allocation import Allocation
from app.models.candidate import CandidateProfile
from app.services.fairness_service import FairnessService

logger = logging.getLogger(__name__)


class FairnessModule:
    """Domain module for fairness monitoring and policy enforcement."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._service = FairnessService()

    async def compute_cycle_fairness(self, cycle_id: int) -> dict[str, Any]:
        """Compute fairness metrics for all allocations in a cycle.

        Returns category distribution, rural/urban ratio, and
        representation percentages.
        """
        alloc_result = await self.db.execute(select(Allocation).where(Allocation.allocation_cycle_id == cycle_id))
        allocations = alloc_result.scalars().all()

        if not allocations:
            return {"cycle_id": cycle_id, "total": 0}

        cand_ids = list(set(a.candidate_id for a in allocations))
        cand_result = await self.db.execute(select(CandidateProfile).where(CandidateProfile.id.in_(cand_ids)))
        candidates = {c.id: c for c in cand_result.scalars().all()}

        alloc_dicts = [{"candidate_id": a.candidate_id, "opportunity_id": a.opportunity_id} for a in allocations]

        metrics = self._service.compute_group_fairness_metrics(alloc_dicts, candidates)
        metrics["cycle_id"] = cycle_id
        return metrics

    async def get_category_distribution(self, cycle_id: int) -> dict[str, dict[str, Any]]:
        """Return per-category allocation counts and percentages."""
        metrics = await self.compute_cycle_fairness(cycle_id)
        total = metrics.get("total", 0)
        dist = metrics.get("category_distribution", {})
        return {
            cat: {
                "count": count,
                "percentage": round(count / total * 100, 1) if total else 0.0,
            }
            for cat, count in dist.items()
        }

    async def get_geographic_distribution(self, cycle_id: int) -> dict[str, dict[str, Any]]:
        """Return per-state allocation counts."""
        alloc_result = await self.db.execute(select(Allocation).where(Allocation.allocation_cycle_id == cycle_id))
        allocations = alloc_result.scalars().all()

        if not allocations:
            return {}

        cand_ids = list(set(a.candidate_id for a in allocations))
        cand_result = await self.db.execute(select(CandidateProfile).where(CandidateProfile.id.in_(cand_ids)))
        candidates = {c.id: c for c in cand_result.scalars().all()}

        state_counts: dict[str, int] = {}
        total = len(allocations)
        for a in allocations:
            cand = candidates.get(a.candidate_id)
            state = cand.state if cand and cand.state else "unknown"
            state_counts[state] = state_counts.get(state, 0) + 1

        return {
            state: {
                "count": count,
                "percentage": round(count / total * 100, 1),
            }
            for state, count in sorted(state_counts.items(), key=lambda x: -x[1])
        }

    def rerank(
        self,
        candidate: CandidateProfile,
        scored: list[tuple[Any, float, dict[str, float]]],
    ) -> list[tuple[Any, float, dict[str, float]]]:
        """Apply fairness-aware re-ranking to scored matches.

        Delegates to the fairness service. This is a synchronous operation
        used during the matching pipeline.
        """
        return self._service.rerank(candidate, scored)
