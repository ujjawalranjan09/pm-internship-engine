"""Constrained allocation service using OR-Tools linear programming."""

import logging
from datetime import datetime, timezone
from typing import Any

from ortools.linear_solver import pywraplp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.allocation import Allocation, AllocationStatus
from app.models.allocation_cycle import AllocationCycle
from app.models.candidate import CandidateProfile
from app.models.match import Match
from app.models.opportunity import Opportunity
from app.models.waitlist import WaitlistEntry

logger = logging.getLogger(__name__)


class AllocationService:
    """Optimal allocation using OR-Tools constraint programming."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def run_allocation(self, cycle_id: int) -> dict[str, Any]:
        """Run the full allocation pipeline for a cycle.

        1. Load all matches above threshold
        2. Build constraint programming model
        3. Solve for optimal allocation
        4. Persist allocations and waitlist entries
        """
        # Load matches
        matches_result = await self.db.execute(
            select(Match)
            .where(Match.score >= 0.1)
            .order_by(Match.score.desc())
        )
        matches = matches_result.scalars().all()

        if not matches:
            logger.warning("No matches found for allocation cycle %d", cycle_id)
            return {"cycle_id": cycle_id, "allocations": 0, "waitlisted": 0}

        # Load opportunities for capacity
        opp_ids = list(set(m.opportunity_id for m in matches))
        opp_result = await self.db.execute(
            select(Opportunity).where(Opportunity.id.in_(opp_ids))
        )
        opportunities = {o.id: o for o in opp_result.scalars().all()}

        # Load candidates
        cand_ids = list(set(m.candidate_id for m in matches))
        cand_result = await self.db.execute(
            select(CandidateProfile).where(CandidateProfile.id.in_(cand_ids))
        )
        candidates = {c.id: c for c in cand_result.scalars().all()}

        # Build and solve the optimization model
        allocations, waitlisted = self._solve_allocation(matches, opportunities, candidates)

        # Persist allocations
        allocated_count = 0
        for match_id, (candidate_id, opportunity_id) in allocations.items():
            match_obj = next((m for m in matches if m.id == match_id), None)
            explanation = match_obj.explanation if match_obj else "Optimal allocation"

            allocation = Allocation(
                candidate_id=candidate_id,
                opportunity_id=opportunity_id,
                match_id=match_id,
                allocation_cycle_id=cycle_id,
                status=AllocationStatus.PENDING,
                explanation=explanation,
                allocated_at=datetime.now(timezone.utc),
            )
            self.db.add(allocation)
            allocated_count += 1

        # Persist waitlist
        waitlist_count = 0
        for position, (candidate_id, opportunity_id, match_id) in enumerate(waitlisted, start=1):
            entry = WaitlistEntry(
                candidate_id=candidate_id,
                opportunity_id=opportunity_id,
                allocation_cycle_id=cycle_id,
                position=position,
                status="waiting",
            )
            self.db.add(entry)
            waitlist_count += 1

        await self.db.flush()
        logger.info(
            "Allocation cycle %d: %d allocated, %d waitlisted",
            cycle_id,
            allocated_count,
            waitlist_count,
        )

        return {
            "cycle_id": cycle_id,
            "allocations": allocated_count,
            "waitlisted": waitlist_count,
        }

    def _solve_allocation(
        self,
        matches: list[Match],
        opportunities: dict[int, Opportunity],
        candidates: dict[int, CandidateProfile],
    ) -> tuple[dict[int, tuple[int, int]], list[tuple[int, int, int]]]:
        """Solve the constrained allocation problem using OR-Tools.

        Maximizes total match score subject to:
        - Each candidate gets at most 1 allocation
        - Each opportunity's capacity is respected
        - Only eligible match pairs are considered

        Returns:
            Tuple of (allocations dict mapping match_id -> (candidate_id, opportunity_id),
                      waitlist entries as (candidate_id, opportunity_id, match_id))
        """
        solver = pywraplp.Solver.CreateSolver("SCIP")
        if solver is None:
            logger.error("Failed to create OR-Tools solver")
            return {}, []

        # Decision variables: x[i] = 1 if match i is selected
        x: dict[int, pywraplp.Variable] = {}
        for match in matches:
            x[match.id] = solver.IntVar(0, 1, f"x_{match.id}")

        # Constraint 1: Each candidate allocated at most once
        candidate_matches: dict[int, list[int]] = {}
        for match in matches:
            candidate_matches.setdefault(match.candidate_id, []).append(match.id)

        for candidate_id, match_ids in candidate_matches.items():
            solver.Add(sum(x[mid] for mid in match_ids) <= 1)

        # Constraint 2: Opportunity capacity limits
        opp_matches: dict[int, list[int]] = {}
        for match in matches:
            opp_matches.setdefault(match.opportunity_id, []).append(match.id)

        for opp_id, match_ids in opp_matches.items():
            capacity = opportunities[opp_id].capacity if opp_id in opportunities else 1
            solver.Add(sum(x[mid] for mid in match_ids) <= capacity)

        # Objective: maximize total weighted score
        objective = solver.Objective()
        for match in matches:
            objective.SetCoefficient(x[match.id], match.score)
        objective.SetMaximization()

        # Solve
        status = solver.Solve()

        allocations: dict[int, tuple[int, int]] = {}
        waitlisted: list[tuple[int, int, int]] = []

        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            for match in matches:
                if x[match.id].solution_value() > 0.5:
                    allocations[match.id] = (match.candidate_id, match.opportunity_id)

            # Build waitlist from top non-allocated matches
            allocated_candidates = set(c for c, _ in allocations.values())
            allocated_opp_counts: dict[int, int] = {}
            for _, opp_id in allocations.values():
                allocated_opp_counts[opp_id] = allocated_opp_counts.get(opp_id, 0) + 1

            for match in matches:
                if match.id in allocations:
                    continue
                # Only waitlist if candidate isn't already allocated
                if match.candidate_id in allocated_candidates:
                    continue
                # Only waitlist if opportunity has capacity
                opp = opportunities.get(match.opportunity_id)
                if opp is None:
                    continue
                current = allocated_opp_counts.get(match.opportunity_id, 0)
                if current < opp.capacity:
                    waitlisted.append((match.candidate_id, match.opportunity_id, match.id))
                    allocated_candidates.add(match.candidate_id)
                    allocated_opp_counts[match.opportunity_id] = current + 1

            logger.info(
                "OR-Tools solution: %d allocations, objective=%.4f",
                len(allocations),
                solver.Objective().Value(),
            )
        else:
            logger.warning("OR-Tools solver status: %d (no feasible solution)", status)

        return allocations, waitlisted
