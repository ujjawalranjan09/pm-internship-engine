"""Tests for the optimizer module."""

import pytest

from app.ml.ranking.optimizer import (
    AllocationOptimizer,
    CandidateProfile,
    optimize_allocation,
)


@pytest.fixture
def sample_candidates():
    """Create sample candidates for optimizer tests."""
    return [
        CandidateProfile(candidate_id="c1", score=0.9, category="general"),
        CandidateProfile(candidate_id="c2", score=0.8, category="sc"),
        CandidateProfile(candidate_id="c3", score=0.5, category="obc"),
        CandidateProfile(candidate_id="c4", score=0.3, category="general"),
    ]


class TestOptimizeAllocation:
    """Tests for optimize_allocation function."""

    def test_basic_allocation(self, sample_candidates):
        result = optimize_allocation(sample_candidates, n_slots=2)
        assert len(result.allocated) == 2
        assert result.allocated[0].score >= result.allocated[1].score

    def test_min_score_filter(self, sample_candidates):
        result = optimize_allocation(sample_candidates, n_slots=10, min_score=0.6)
        assert len(result.allocated) == 2
        assert all(c.score >= 0.6 for c in result.allocated)

    def test_unallocated_candidates(self, sample_candidates):
        result = optimize_allocation(sample_candidates, n_slots=2)
        assert len(result.unallocated) == 2

    def test_metadata(self, sample_candidates):
        result = optimize_allocation(sample_candidates, n_slots=2)
        assert result.metadata["n_candidates"] == 4
        assert result.metadata["n_slots"] == 2
        assert result.metadata["n_allocated"] == 2


class TestAllocationOptimizer:
    """Tests for AllocationOptimizer class."""

    def test_run_allocation(self, sample_candidates):
        optimizer = AllocationOptimizer(n_slots=2, min_score=0.4)
        result = optimizer.run(sample_candidates)
        assert len(result.allocated) == 2

    def test_greedy_fallback_config(self, sample_candidates):
        optimizer = AllocationOptimizer(n_slots=2, use_greedy_fallback=True)
        assert optimizer.use_greedy_fallback is True
        assert optimizer.time_limit_seconds == 60.0

    def test_run_from_scores(self, sample_candidates):
        optimizer = AllocationOptimizer(n_slots=3)
        ids = [c.candidate_id for c in sample_candidates]
        scores = [c.score for c in sample_candidates]
        result = optimizer.run_from_scores(ids, scores)
        assert len(result.allocated) == 3
