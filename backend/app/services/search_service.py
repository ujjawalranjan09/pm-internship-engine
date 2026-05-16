"""Full-text and vector-similarity search over opportunities."""

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.opportunity import Opportunity

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def keyword_search(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        limit: int = 20,
    ) -> list[Opportunity]:
        """Simple ilike keyword search across title, description, and company."""
        stmt = select(Opportunity).where(Opportunity.is_active == True)  # noqa: E712
        if query:
            pattern = f"%{query}%"
            from sqlalchemy import or_
            stmt = stmt.where(
                or_(
                    Opportunity.title.ilike(pattern),
                    Opportunity.description.ilike(pattern),
                    Opportunity.company_name.ilike(pattern),
                )
            )
        if filters:
            if sector := filters.get("sector"):
                stmt = stmt.where(Opportunity.sector == sector)
            if state := filters.get("state"):
                stmt = stmt.where(Opportunity.state == state)
        stmt = stmt.limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_sector(
        self, sector: str, limit: int = 50
    ) -> list[Opportunity]:
        result = await self.db.execute(
            select(Opportunity)
            .where(Opportunity.sector == sector, Opportunity.is_active == True)  # noqa: E712
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_available(
        self,
        filters: dict[str, Any] | None = None,
        limit: int = 100,
    ) -> list[Opportunity]:
        stmt = (
            select(Opportunity)
            .where(Opportunity.is_active == True)  # noqa: E712
            .where(Opportunity.filled_seats < Opportunity.total_seats)
        )
        if filters:
            if sector := filters.get("sector"):
                stmt = stmt.where(Opportunity.sector == sector)
        stmt = stmt.limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
