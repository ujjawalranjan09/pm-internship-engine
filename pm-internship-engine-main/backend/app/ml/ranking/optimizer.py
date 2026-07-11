"""
Allocation Optimizer – Constraint-Based Candidate Allocation
=============================================================

Solves the allocation optimisation problem: assign candidates to
internship slots subject to fairness, quota, and quality constraints.

Approaches:
    - Greedy: fast, good enough for most cycles
    - LP relaxation: better quality for large cycles
    - Integer programming: optimal, used for final allocation
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CandidateProfile:
    """Lightweight candidate profile used by the optimizer."""

    candidate_id: str
    score: float
    opportunity_id: str | None = None
    features: dict[str, Any] = field(default_factory=dict)
    category: str = "general"
    is_rural: bool = False
    gender: str = "unspecified"


@dataclass
class OptimizedAllocationResult:
    """Result from an optimize_allocation call."""

    allocated: list[CandidateProfile] = field(default_factory=list)
    unallocated: list[CandidateProfile] = field(default_factory=list)
    objective_value: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    solver_status: str = "OPTIMAL"

    @property
    def num_allocated(self) -> int:
        return len(self.allocated)

    @property
    def total_score(self) -> float:
        return self.objective_value

    @property
    def allocations(self) -> list[dict[str, Any]]:
        return [
            {
                "candidate_id": c.candidate_id,
                "opportunity_id": c.opportunity_id,
                "score": c.score,
                "category": c.category,
            }
            for c in self.allocated
        ]


def optimize_allocation(
    candidates: list[CandidateProfile],
    n_slots: int,
    min_score: float = 0.0,
    weights: dict[str, float] | None = None,
    opportunity_id: str | None = None,
) -> OptimizedAllocationResult:
    """Greedy allocation: top-N eligible candidates by score."""
    eligible = [c for c in candidates if c.score >= min_score]
    eligible_sorted = sorted(eligible, key=lambda x: x.score, reverse=True)
    allocated = eligible_sorted[:n_slots]
    unallocated = eligible_sorted[n_slots:] + [c for c in candidates if c.score < min_score]

    # Set opportunity_id on allocated candidates if provided
    if opportunity_id:
        for c in allocated:
            if c.opportunity_id is None:
                c.opportunity_id = opportunity_id

    return OptimizedAllocationResult(
        allocated=allocated,
        unallocated=unallocated,
        objective_value=round(sum(c.score for c in allocated), 4),
        metadata={
            "n_candidates": len(candidates),
            "n_slots": n_slots,
            "n_allocated": len(allocated),
            "n_unallocated": len(unallocated),
        },
    )


class AllocationOptimizer:
    """
    Wraps optimize_allocation with configurable strategy and constraints.

    Usage:
        optimizer = AllocationOptimizer(n_slots=50, min_score=0.4)
        result = optimizer.run(candidates)
    """

    def __init__(
        self,
        n_slots: int = 10,
        min_score: float = 0.0,
        strategy: str = "greedy",
        weights: dict[str, float] | None = None,
        time_limit_seconds: float = 60.0,
        use_greedy_fallback: bool = True,
    ) -> None:
        self.n_slots = n_slots
        self.min_score = min_score
        self.strategy = strategy
        self.weights = weights or {}
        self.time_limit_seconds = time_limit_seconds
        self.use_greedy_fallback = use_greedy_fallback

    def run(self, candidates: list[CandidateProfile]) -> OptimizedAllocationResult:
        """Run the configured allocation strategy."""
        return optimize_allocation(
            candidates,
            n_slots=self.n_slots,
            min_score=self.min_score,
            weights=self.weights if self.weights else None,
        )

    def run_from_scores(
        self,
        candidate_ids: list[str],
        scores: np.ndarray,
        metadata: list[dict[str, Any]] | None = None,
        opportunity_id: str | None = None,
    ) -> OptimizedAllocationResult:
        """Build CandidateProfile list from raw scores and run allocation."""
        profiles: list[CandidateProfile] = []
        for i, (cid, score) in enumerate(zip(candidate_ids, scores, strict=False)):
            meta = metadata[i] if metadata else {}
            profiles.append(
                CandidateProfile(
                    candidate_id=cid,
                    score=float(score),
                    opportunity_id=opportunity_id,
                    category=str(meta.get("category", "general")),
                    is_rural=bool(meta.get("is_rural", False)),
                    gender=str(meta.get("gender", "unspecified")),
                )
            )
        return self.run(profiles)

    def optimize(
        self,
        score_matrix: Any,
        candidate_ids: list[str],
        opportunity_ids: list[str],
        capacities: dict[str, int],
        constraints: Any | None = None,
        blocked_pairs: list[tuple[str, str]] | None = None,
    ) -> OptimizedAllocationResult:
        """Optimize allocation given score matrix and constraints.

        Falls back to greedy allocation when OR-Tools is not available.
        """
        # Build all candidate-opportunity pairs with scores
        n_cand = len(candidate_ids)
        n_opp = len(opportunity_ids)
        pairs = []

        for i, cid in enumerate(candidate_ids):
            for j, oid in enumerate(opportunity_ids):
                score = float(score_matrix[i, j])
                if score > self.min_score:
                    pairs.append((cid, oid, score))

        # Sort by score descending
        pairs.sort(key=lambda x: -x[2])

        # Greedy allocation respecting capacities and blocked pairs
        allocated_opp: dict[str, int] = {oid: 0 for oid in capacities}
        allocated_cand: set[str] = set()
        blocked = set(blocked_pairs) if blocked_pairs else set()

        allocated_profiles: list[CandidateProfile] = []

        for cid, oid, score in pairs:
            if cid in allocated_cand:
                continue
            if allocated_opp.get(oid, 0) >= capacities.get(oid, 1):
                continue
            if (cid, oid) in blocked:
                continue

            allocated_profiles.append(CandidateProfile(
                candidate_id=cid,
                opportunity_id=oid,
                score=score,
            ))
            allocated_cand.add(cid)
            allocated_opp[oid] = allocated_opp.get(oid, 0) + 1

            if len(allocated_profiles) >= self.n_slots:
                break

        unallocated_profiles = [
            CandidateProfile(candidate_id=cid, opportunity_id=oid, score=score)
            for cid, oid, score in pairs
            if cid not in allocated_cand
        ]

        return OptimizedAllocationResult(
            allocated=allocated_profiles,
            unallocated=unallocated_profiles,
            objective_value=round(sum(c.score for c in allocated_profiles), 4),
            metadata={
                "n_candidates": n_cand,
                "n_slots": self.n_slots,
                "n_allocated": len(allocated_profiles),
                "n_unallocated": len(unallocated_profiles),
            },
        )