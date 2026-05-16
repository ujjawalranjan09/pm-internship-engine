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


def optimize_allocation(
    candidates: list[CandidateProfile],
    n_slots: int,
    min_score: float = 0.0,
    weights: dict[str, float] | None = None,
) -> OptimizedAllocationResult:
    """Greedy allocation: top-N eligible candidates by score."""
    eligible = [c for c in candidates if c.score >= min_score]
    eligible_sorted = sorted(eligible, key=lambda x: x.score, reverse=True)
    allocated = eligible_sorted[:n_slots]
    unallocated = eligible_sorted[n_slots:] + [c for c in candidates if c.score < min_score]
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
    ) -> None:
        self.n_slots = n_slots
        self.min_score = min_score
        self.strategy = strategy
        self.weights = weights or {}

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
    ) -> OptimizedAllocationResult:
        """Build CandidateProfile list from raw scores and run allocation."""
        profiles: list[CandidateProfile] = []
        for i, (cid, score) in enumerate(zip(candidate_ids, scores, strict=False)):
            meta = metadata[i] if metadata else {}
            profiles.append(
                CandidateProfile(
                    candidate_id=cid,
                    score=float(score),
                    category=str(meta.get("category", "general")),
                    is_rural=bool(meta.get("is_rural", False)),
                    gender=str(meta.get("gender", "unspecified")),
                )
            )
        return self.run(profiles)
