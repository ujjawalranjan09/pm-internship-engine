"""Allocation domain module — cycle management and allocation runs."""

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.allocation import Allocation, AllocationStatus
from app.models.allocation_cycle import AllocationCycle, CycleStatus
from app.models.waitlist import WaitlistEntry
from app.services.allocation_service import AllocationService

logger = logging.getLogger(__name__)


class AllocationModule:
    """Domain module for allocation cycle management."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._service = AllocationService(db)

    async def create_cycle(self, name: str, config: dict[str, Any] | None = None) -> AllocationCycle:
        """Create a new allocation cycle in draft state."""
        cycle = AllocationCycle(
            name=name,
            status=CycleStatus.DRAFT,
            config=config,
        )
        self.db.add(cycle)
        await self.db.flush()
        await self.db.refresh(cycle)
        logger.info("Created allocation cycle %d: %s", cycle.id, name)
        return cycle

    async def run_cycle(self, cycle_id: int) -> dict[str, Any]:
        """Execute an allocation cycle.

        Transitions the cycle to RUNNING, runs the optimizer, then marks
        COMPLETED or FAILED.
        """
        cycle = await self.get_cycle(cycle_id)
        if cycle is None:
            raise ValueError(f"Allocation cycle {cycle_id} not found")
        if cycle.status != CycleStatus.DRAFT:
            raise ValueError(f"Cycle {cycle_id} is in status '{cycle.status.value}', expected 'draft'")

        cycle.status = CycleStatus.RUNNING
        cycle.started_at = datetime.now(UTC)
        await self.db.flush()

        try:
            result = await self._service.run_allocation(cycle_id)
            cycle.status = CycleStatus.COMPLETED
            cycle.completed_at = datetime.now(UTC)
            await self.db.flush()
            logger.info("Allocation cycle %d completed: %s", cycle_id, result)
            return result
        except Exception:
            cycle.status = CycleStatus.FAILED
            await self.db.flush()
            raise

    async def get_cycle(self, cycle_id: int) -> AllocationCycle | None:
        """Fetch an allocation cycle by ID."""
        result = await self.db.execute(select(AllocationCycle).where(AllocationCycle.id == cycle_id))
        return result.scalar_one_or_none()

    async def list_cycles(self, *, status: CycleStatus | None = None, limit: int = 20) -> list[AllocationCycle]:
        """List allocation cycles, newest first."""
        query = select(AllocationCycle)
        if status:
            query = query.where(AllocationCycle.status == status)
        query = query.order_by(AllocationCycle.created_at.desc()).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_cycle_allocations(self, cycle_id: int) -> list[Allocation]:
        """Get all allocations for a cycle."""
        result = await self.db.execute(
            select(Allocation).where(Allocation.allocation_cycle_id == cycle_id).order_by(Allocation.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_cycle_waitlist(self, cycle_id: int) -> list[WaitlistEntry]:
        """Get the waitlist for a cycle, ordered by position."""
        result = await self.db.execute(
            select(WaitlistEntry).where(WaitlistEntry.allocation_cycle_id == cycle_id).order_by(WaitlistEntry.position)
        )
        return list(result.scalars().all())

    async def get_cycle_stats(self, cycle_id: int) -> dict[str, Any]:
        """Compute aggregate statistics for a cycle."""
        alloc_result = await self.db.execute(
            select(
                func.count(Allocation.id).label("total"),
                func.count().filter(Allocation.status == AllocationStatus.CONFIRMED).label("confirmed"),
                func.count().filter(Allocation.status == AllocationStatus.DECLINED).label("declined"),
            ).where(Allocation.allocation_cycle_id == cycle_id)
        )
        row = alloc_result.one()

        wl_result = await self.db.execute(
            select(func.count(WaitlistEntry.id)).where(WaitlistEntry.allocation_cycle_id == cycle_id)
        )
        waitlisted = wl_result.scalar() or 0

        return {
            "cycle_id": cycle_id,
            "total_allocated": row.total or 0,
            "total_confirmed": row.confirmed or 0,
            "total_declined": row.declined or 0,
            "total_waitlisted": waitlisted,
        }

    async def update_allocation_status(
        self,
        allocation_id: int,
        new_status: AllocationStatus,
        *,
        explanation: str | None = None,
    ) -> Allocation | None:
        """Update the status of a single allocation."""
        result = await self.db.execute(select(Allocation).where(Allocation.id == allocation_id))
        allocation = result.scalar_one_or_none()
        if allocation is None:
            return None

        allocation.status = new_status
        if explanation:
            allocation.explanation = explanation
        await self.db.flush()
        await self.db.refresh(allocation)
        logger.info("Allocation %d status -> %s", allocation_id, new_status.value)
        return allocation
