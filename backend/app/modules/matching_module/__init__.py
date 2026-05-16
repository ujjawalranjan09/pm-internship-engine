"""Matching domain module — orchestrates matching pipeline."""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import CandidateProfile
from app.models.match import Match
from app.models.opportunity import Opportunity
from app.services.matching_service import MatchingService

logger = logging.getLogger(__name__)


class MatchingModule:
    """Domain module for candidate-opportunity matching.

    Wraps MatchingService and adds domain-level orchestration,
    batch processing, and result aggregation.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._service = MatchingService(db)

    async def get_recommendations(
        self, candidate_id: int, top_k: int = 10
    ) -> list[Match]:
        """Get top-K opportunity recommendations for a candidate.

        Returns cached matches if available, otherwise runs the pipeline.
        """
        matches = await self._service.get_recommendations(candidate_id, top_k)
        logger.info(
            "Returned %d recommendations for candidate %d",
            len(matches),
            candidate_id,
        )
        return matches

    async def run_batch(self) -> dict[str, Any]:
        """Run matching for all active candidates.

        Returns aggregate stats: candidates processed, opportunities considered,
        total matches generated.
        """
        result = await self._service.run_batch_matching()
        logger.info("Batch matching complete: %s", result)
        return result

    async def get_match_details(self, match_id: int) -> Match | None:
        """Retrieve a single match with full details."""
        from sqlalchemy import select

        result = await self.db.execute(
            select(Match).where(Match.id == match_id)
        )
        return result.scalar_one_or_none()

    async def get_candidate_matches(
        self, candidate_id: int, *, status: str | None = None, limit: int = 50
    ) -> list[Match]:
        """Get all matches for a candidate, optionally filtered by status."""
        from sqlalchemy import select

        query = select(Match).where(Match.candidate_id == candidate_id)
        if status:
            query = query.where(Match.status == status)
        query = query.order_by(Match.score.desc()).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def invalidate_cache(self, candidate_id: int) -> int:
        """Delete cached matches for a candidate so next request re-runs pipeline."""
        from sqlalchemy import delete

        result = await self.db.execute(
            delete(Match).where(Match.candidate_id == candidate_id)
        )
        count = result.rowcount  # type: ignore[union-attr]
        await self.db.flush()
        logger.info("Invalidated %d cached matches for candidate %d", count, candidate_id)
        return count
