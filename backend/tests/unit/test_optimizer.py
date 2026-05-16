"""Tests for the optimizer module."""

import numpy as np
import pandas as pd
import pytest

from app.ml.ranking.optimizer import (
    AllocationOptimizer,
    CandidateProfile,
    OptimizationConstraints,
    OpportunitySlot,
    build_allocation_problem,
    export_results,
)


@pytest.fixture
def sample_data():
    """Create sample data for optimizer tests."""
    score_matrix = pd.DataFrame(
        [[0.9, 0.3, 0.1], [0.2, 0.8, 0.4], [0.5, 0.6, 0.9]],
        index=["c1", "c2", "c3"],
        columns=["o1", "o2", "o3"],
    )
    candidates = [
        CandidateProfile(candidate_id="c1", district="A", category="general"),
        CandidateProfile(candidate_id="c2", district="B", category="sc"),
        CandidateProfile(candidate_id="c3", district="A", category="obc"),
    ]
    opportunities = [
        OpportunitySlot(opportunity_id="o1", capacity=2),
        OpportunitySlot(opportunity_id="o2", capacity=1),
        OpportunitySlot(opportunity_id="o3", capacity=1),
    ]
    return score_matrix, candidates, opportunities


class TestAllocationOptimizer:
    """Tests for the allocation optimizer."""

    def test_basic_allocation(self, sample_data):
        score_matrix, candidates, opportunities = sample_data
        result = build_allocation_problem(score_matrix, candidates, opportunities)
        assert len(result.allocations) > 0
        assert result.solver_status in ("OPTIMAL", "FEASIBLE", "GREEDY_FALLBACK")

    def test_each_candidate_at_most_one(self, sample_data):
        score_matrix, candidates, opportunities = sample_data
        result = build_allocation_problem(score_matrix, candidates, opportunities)
        assigned = [a["candidate_id"] for a in result.allocations]
        # Each candidate appears at most once
        assert len(assigned) == len(set(assigned))

    def test_capacity_respected(self, sample_data):
        score_matrix, candidates, opportunities = sample_data
        result = build_allocation_problem(score_matrix, candidates, opportunities)
        opp_counts = {}
        for a in result.allocations:
            oid = a["opportunity_id"]
            opp_counts[oid] = opp_counts.get(oid, 0) + 1
        # o2 has capacity 1, o3 has capacity 1
        assert opp_counts.get("o2", 0) <= 1
        assert opp_counts.get("o3", 0) <= 1

    def test_waitlist_for_unassigned(self, sample_data):
        score_matrix, candidates, opportunities = sample_data
        constraints = OptimizationConstraints(max_per_candidate=1)
        result = build_allocation_problem(score_matrix, candidates, opportunities, constraints)
        # All candidates should be either allocated or waitlisted
        allocated_ids = {a["candidate_id"] for a in result.allocations}
        waitlisted_ids = {w["candidate_id"] for w in result.waitlist}
        all_ids = allocated_ids | waitlisted_ids
        assert "c1" in all_ids
        assert "c2" in all_ids
        assert "c3" in all_ids

    def test_explanations_present(self, sample_data):
        score_matrix, candidates, opportunities = sample_data
        result = build_allocation_problem(score_matrix, candidates, opportunities)
        for a in result.allocations:
            cid = a["candidate_id"]
            assert cid in result.explanations


class TestExportResults:
    """Tests for export_results function."""

    def test_export_structure(self, sample_data):
        score_matrix, candidates, opportunities = sample_data
        result = build_allocation_problem(score_matrix, candidates, opportunities)
        exported = export_results(result)
        assert "allocations" in exported
        assert "waitlist" in exported
        assert "summary" in exported
        assert "explanations" in exported
        assert "metrics" in exported

    def test_summary_fields(self, sample_data):
        score_matrix, candidates, opportunities = sample_data
        result = build_allocation_problem(score_matrix, candidates, opportunities)
        exported = export_results(result)
        summary = exported["summary"]
        assert "total_allocations" in summary
        assert "total_waitlisted" in summary
        assert "allocation_rate" in summary
        assert "solver_status" in summary
