"""Constrained allocation service using OR-Tools linear programming."""

import logging
import os
import sys
from datetime import UTC, datetime
from typing import Any

# Delay OR-Tools import to handle Windows DLL loading issues
_pywraplp = None
_ortools_import_error = None

def _get_pywraplp():
    """Lazily import pywraplp to handle Windows DLL issues."""
    global _pywraplp, _ortools_import_error
    if _pywraplp is not None or _ortools_import_error is not None:
        return _pywraplp

    # On Windows, add the ortools libs directory to DLL search path
    if sys.platform == "win32":
        try:
            import site
            site_packages = site.getsitepackages()[0]
            ortools_libs = os.path.join(site_packages, "ortools", ".libs")
            if os.path.exists(ortools_libs):
                os.add_dll_directory(ortools_libs)
        except Exception:
            pass

    try:
        from ortools.linear_solver import pywraplp
        _pywraplp = pywraplp
    except Exception as e:
        _ortools_import_error = e
        logger = logging.getLogger(__name__)
        logger.warning("OR-Tools not available: %s. Allocation will use greedy fallback.", e)

    return _pywraplp


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.allocation import Allocation, AllocationStatus
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
        """Run the full allocation pipeline for a cycle."""
        matches_result = await self.db.execute(select(Match).where(Match.score >= 0.1).order_by(Match.score.desc()))
        matches = list(matches_result.scalars().all())

        if not matches:
            logger.warning("No matches found for allocation cycle %d", cycle_id)
            return {"cycle_id": cycle_id, "allocations": 0, "waitlisted": 0}

        opp_ids = list(set(m.opportunity_id for m in matches))
        opp_result = await self.db.execute(select(Opportunity).where(Opportunity.id.in_(opp_ids)))
        opportunities = {o.id: o for o in opp_result.scalars().all()}

        cand_ids = list(set(m.candidate_id for m in matches))
        cand_result = await self.db.execute(select(CandidateProfile).where(CandidateProfile.id.in_(cand_ids)))
        candidates = {c.id: c for c in cand_result.scalars().all()}

        allocations, waitlisted = self._solve_allocation(matches, opportunities, candidates)

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
                allocated_at=datetime.now(UTC),
            )
            self.db.add(allocation)
            allocated_count += 1

        waitlist_count = 0
        for position, (candidate_id, opportunity_id, _match_id) in enumerate(waitlisted, start=1):
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
        """Solve the constrained allocation problem using OR-Tools."""
        pywraplp = _get_pywraplp()
        if pywraplp is None:
            logger.warning("OR-Tools not available, using greedy fallback")
            return self._greedy_allocation(matches, opportunities, candidates)

        solver = pywraplp.Solver.CreateSolver("SCIP")
        if solver is None:
            logger.error("Failed to create OR-Tools solver, using greedy fallback")
            return self._greedy_allocation(matches, opportunities, candidates)

        x: dict[int, pywraplp.Variable] = {}

        candidate_matches: dict[int, list[int]] = {}
        for match in matches:
            candidate_matches.setdefault(match.candidate_id, []).append(match.id)

        for _candidate_id, match_ids in candidate_matches.items():
            solver.Add(sum(x[mid] for mid in match_ids) <= 1)

        opp_matches: dict[int, list[int]] = {}
        for match in matches:
            opp_matches.setdefault(match.opportunity_id, []).append(match.id)

        for opp_id, match_ids in opp_matches.items():
            capacity = opportunities[opp_id].capacity if opp_id in opportunities else 1
            solver.Add(sum(x[mid] for mid in match_ids) <= capacity)

        objective = solver.Objective()
        for match in matches:
            objective.SetCoefficient(x[match.id], match.score)
        objective.SetMaximization()

        status = solver.Solve()

        allocations: dict[int, tuple[int, int]] = {}
        waitlisted: list[tuple[int, int, int]] = []

        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            for match in matches:
                if x[match.id].solution_value() > 0.5:
                    allocations[match.id] = (match.candidate_id, match.opportunity_id)

            allocated_candidates = set(c for c, _ in allocations.values())
            allocated_opp_counts: dict[int, int] = {}
            for _, opp_id in allocations.values():
                allocated_opp_counts[opp_id] = allocated_opp_counts.get(opp_id, 0) + 1

            for match in matches:
                if match.id in allocations:
                    continue
                if match.candidate_id in allocated_candidates:
                    continue
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

    def _greedy_allocation(
        self,
        matches: list[Match],
        opportunities: dict[int, Opportunity],
        candidates: dict[int, CandidateProfile],
    ) -> tuple[dict[int, tuple[int, int]], list[tuple[int, int, int]]]:
        """Greedy fallback allocation when OR-Tools is unavailable."""
        # Sort matches by score descending
        sorted_matches = sorted(matches, key=lambda m: m.score, reverse=True)

        allocated_candidates = set()
        allocated_opp_counts: dict[int, int] = {}
        allocations: dict[int, tuple[int, int]] = {}
        waitlisted: list[tuple[int, int, int]] = []

        for match in sorted_matches:
            if match.candidate_id in allocated_candidates:
                continue
            opp = opportunities.get(match.opportunity_id)
            if opp is None:
                continue
            current = allocated_opp_counts.get(match.opportunity_id, 0)
            if current < opp.capacity:
                allocations[match.id] = (match.candidate_id, match.opportunity_id)
                allocated_candidates.add(match.candidate_id)
                allocated_opp_counts[match.opportunity_id] = current + 1
            else:
                waitlisted.append((match.candidate_id, match.opportunity_id, match.id))

        logger.info("Greedy fallback: %d allocations, %d waitlisted", len(allocations), len(waitlisted))
        return allocations, waitlisted
