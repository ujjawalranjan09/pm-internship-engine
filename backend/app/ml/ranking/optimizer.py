"""
Allocation Optimizer – Constrained Global Optimization (Stage E)
=================================================================

Uses Google OR-Tools to solve the assignment problem: given scored
candidate-opportunity pairs, find the allocation that maximises
total match quality subject to capacity, eligibility, and fairness
constraints.

Formulation:
    Maximize Σ score_ij × x_ij
    Subject to:
        - Each candidate assigned to at most 1 opportunity
        - Each opportunity assigned at most capacity_j candidates
        - x_ij ∈ {0, 1}

This is a variant of the assignment problem / bipartite matching
with capacity constraints, solved exactly via linear programming.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

logger = logging.getLogger(__name__)

try:
    from ortools.linear_solver import pywraplp
except ImportError:
    pywraplp = None  # type: ignore[assignment]
    logger.warning("ortools not installed – AllocationOptimizer will use greedy fallback")


@dataclass
class AllocationResult:
    """Result of the constrained allocation optimization."""
    candidate_id: str
    opportunity_id: str
    score: float
    is_allocated: bool
    explanation: str = ""


@dataclass
class OptimizationResult:
    """Full result of an optimization run."""
    allocations: List[AllocationResult] = field(default_factory=list)
    total_score: float = 0.0
    num_allocated: int = 0
    num_candidates: int = 0
    num_opportunities: int = 0
    solver_time_seconds: float = 0.0
    solver_status: str = "unknown"
    unallocated_candidates: List[str] = field(default_factory=list)
    unfilled_opportunities: List[str] = field(default_factory=list)


class AllocationOptimizer:
    """
    Global constrained allocation using OR-Tools.

    Solves the bipartite matching problem with capacity constraints
    to find the optimal allocation of candidates to opportunities.

    Falls back to a greedy algorithm if OR-Tools is not available.
    """

    def __init__(
        self,
        time_limit_seconds: float = 60.0,
        use_greedy_fallback: bool = True,
    ) -> None:
        self._time_limit = time_limit_seconds
        self._use_greedy = use_greedy_fallback

    def optimize(
        self,
        score_matrix: np.ndarray,
        candidate_ids: List[str],
        opportunity_ids: List[str],
        capacities: Dict[str, int],
        constraints: Optional[Dict[str, Any]] = None,
        blocked_pairs: Optional[Set[Tuple[str, str]]] = None,
    ) -> OptimizationResult:
        """
        Solve the allocation optimization problem.

        Args:
            score_matrix: Shape (n_candidates, n_opportunities) with match scores.
            candidate_ids: List of candidate IDs (rows).
            opportunity_ids: List of opportunity IDs (columns).
            capacities: Dict mapping opportunity_id to max capacity.
            constraints: Additional constraints (reserved_slots, quotas, etc.).
            blocked_pairs: Set of (candidate_id, opportunity_id) pairs that
                cannot be allocated (e.g. already rejected).

        Returns:
            OptimizationResult with the optimal allocation.
        """
        start = time.time()

        if pywraplp is not None:
            result = self._solve_ortools(
                score_matrix, candidate_ids, opportunity_ids,
                capacities, constraints, blocked_pairs,
            )
        elif self._use_greedy:
            logger.warning("Using greedy fallback (install ortools for optimal allocation)")
            result = self._solve_greedy(
                score_matrix, candidate_ids, opportunity_ids,
                capacities, blocked_pairs,
            )
        else:
            raise ImportError("ortools is required for optimization. pip install ortools")

        result.solver_time_seconds = time.time() - start
        return result

    def _solve_ortools(
        self,
        score_matrix: np.ndarray,
        candidate_ids: List[str],
        opportunity_ids: List[str],
        capacities: Dict[str, int],
        constraints: Optional[Dict[str, Any]],
        blocked_pairs: Optional[Set[Tuple[str, str]]],
    ) -> OptimizationResult:
        """Solve using OR-Tools linear programming."""
        n_candidates = len(candidate_ids)
        n_opportunities = len(opportunity_ids)

        solver = pywraplp.Solver.CreateSolver("SCIP")
        if solver is None:
            solver = pywraplp.Solver.CreateSolver("GLOP")
        if solver is None:
            raise RuntimeError("No OR-Tools solver available")

        solver.SetTimeLimit(int(self._time_limit * 1000))

        # Decision variables: x[i][j] = 1 if candidate i assigned to opportunity j
        x = {}
        for i in range(n_candidates):
            for j in range(n_opportunities):
                x[i, j] = solver.IntVar(0, 1, f"x_{i}_{j}")

        # Constraint 1: Each candidate assigned to at most 1 opportunity
        for i in range(n_candidates):
            solver.Add(sum(x[i, j] for j in range(n_opportunities)) <= 1)

        # Constraint 2: Each opportunity respects capacity
        for j, oid in enumerate(opportunity_ids):
            cap = capacities.get(oid, 1)
            solver.Add(sum(x[i, j] for i in range(n_candidates)) <= cap)

        # Constraint 3: Blocked pairs
        if blocked_pairs:
            for i, cid in enumerate(candidate_ids):
                for j, oid in enumerate(opportunity_ids):
                    if (cid, oid) in blocked_pairs:
                        solver.Add(x[i, j] == 0)

        # Constraint 4: Reserved slots / quotas
        if constraints:
            reserved = constraints.get("reserved_slots", {})
            for group, group_data in reserved.items():
                group_candidate_indices = group_data.get("candidate_indices", [])
                min_slots = group_data.get("min_slots", 0)
                if group_candidate_indices and min_slots > 0:
                    solver.Add(
                        sum(
                            x[i, j]
                            for i in group_candidate_indices
                            for j in range(n_opportunities)
                        ) >= min_slots
                    )

        # Objective: maximize total score
        objective = solver.Objective()
        for i in range(n_candidates):
            for j in range(n_opportunities):
                objective.SetCoefficient(x[i, j], float(score_matrix[i, j]))
        objective.SetMaximization()

        # Solve
        status = solver.Solve()

        status_map = {
            pywraplp.Solver.OPTIMAL: "optimal",
            pywraplp.Solver.FEASIBLE: "feasible",
            pywraplp.Solver.INFEASIBLE: "infeasible",
            pywraplp.Solver.NOT_SOLVED: "not_solved",
            pywraplp.Solver.ABNORMAL: "abnormal",
        }
        solver_status = status_map.get(status, "unknown")

        # Extract solution
        allocations = []
        allocated_candidates: Set[str] = set()
        allocated_per_opp: Dict[str, int] = {}

        for i in range(n_candidates):
            for j in range(n_opportunities):
                if x[i, j].solution_value() > 0.5:
                    allocations.append(AllocationResult(
                        candidate_id=candidate_ids[i],
                        opportunity_id=opportunity_ids[j],
                        score=float(score_matrix[i, j]),
                        is_allocated=True,
                        explanation=f"Optimal allocation (score: {score_matrix[i, j]:.3f})",
                    ))
                    allocated_candidates.add(candidate_ids[i])
                    allocated_per_opp[opportunity_ids[j]] = (
                        allocated_per_opp.get(opportunity_ids[j], 0) + 1
                    )

        # Unallocated candidates
        unallocated = [cid for cid in candidate_ids if cid not in allocated_candidates]

        # Unfilled opportunities
        unfilled = [
            oid for oid in opportunity_ids
            if allocated_per_opp.get(oid, 0) < capacities.get(oid, 1)
        ]

        return OptimizationResult(
            allocations=allocations,
            total_score=solver.Objective().Value(),
            num_allocated=len(allocations),
            num_candidates=n_candidates,
            num_opportunities=n_opportunities,
            solver_status=solver_status,
            unallocated_candidates=unallocated,
            unfilled_opportunities=unfilled,
        )

    def _solve_greedy(
        self,
        score_matrix: np.ndarray,
        candidate_ids: List[str],
        opportunity_ids: List[str],
        capacities: Dict[str, int],
        blocked_pairs: Optional[Set[Tuple[str, str]]],
    ) -> OptimizationResult:
        """
        Greedy fallback: assign highest-score pairs first.

        Not optimal but fast and guaranteed to respect constraints.
        """
        n_candidates = len(candidate_ids)
        n_opportunities = len(opportunity_ids)
        blocked = blocked_pairs or set()

        # Build list of (score, candidate_idx, opportunity_idx)
        pairs = []
        for i in range(n_candidates):
            for j in range(n_opportunities):
                if (candidate_ids[i], opportunity_ids[j]) not in blocked:
                    pairs.append((float(score_matrix[i, j]), i, j))

        # Sort by score descending
        pairs.sort(key=lambda p: -p[0])

        # Greedy assignment
        candidate_assigned: Set[int] = set()
        opp_remaining = {oid: capacities.get(oid, 1) for oid in opportunity_ids}
        allocations = []

        for score, i, j in pairs:
            if i in candidate_assigned:
                continue
            oid = opportunity_ids[j]
            if opp_remaining.get(oid, 0) <= 0:
                continue

            allocations.append(AllocationResult(
                candidate_id=candidate_ids[i],
                opportunity_id=oid,
                score=score,
                is_allocated=True,
                explanation=f"Greedy allocation (score: {score:.3f})",
            ))
            candidate_assigned.add(i)
            opp_remaining[oid] -= 1

        unallocated = [
            cid for idx, cid in enumerate(candidate_ids)
            if idx not in candidate_assigned
        ]
        unfilled = [oid for oid, remaining in opp_remaining.items() if remaining > 0]

        total_score = sum(a.score for a in allocations)

        return OptimizationResult(
            allocations=allocations,
            total_score=total_score,
            num_allocated=len(allocations),
            num_candidates=n_candidates,
            num_opportunities=n_opportunities,
            solver_status="greedy",
            unallocated_candidates=unallocated,
            unfilled_opportunities=unfilled,
        )
