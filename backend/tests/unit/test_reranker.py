"""Tests for the reranker module.

These are pure unit tests that don't require database access.
Tests match the actual Reranker API: rerank(scored_list, candidate_metadata, district_counts)
"""

import pytest

from app.ml.ranking.reranker import (
    FairnessReranker,
    RerankerConfig,
    RerankedCandidate,
)


@pytest.fixture
def sample_scored_candidates():
    """Create sample scored candidates for reranker tests."""
    return [
        {"candidate_id": "c1", "opportunity_id": "o1", "score": 0.8, "rank": 1},
        {"candidate_id": "c2", "opportunity_id": "o1", "score": 0.7, "rank": 2},
        {"candidate_id": "c3", "opportunity_id": "o1", "score": 0.6, "rank": 3},
        {"candidate_id": "c4", "opportunity_id": "o1", "score": 0.5, "rank": 4},
        {"candidate_id": "c5", "opportunity_id": "o1", "score": 0.9, "rank": 5},
    ]


@pytest.fixture
def candidate_metadata():
    """Create candidate metadata for reranker tests."""
    return {
        "c1": {"district": "A", "social_category": "general", "is_rural": False, "gender": "male"},
        "c2": {"district": "B", "social_category": "sc", "is_rural": True, "gender": "female"},
        "c3": {"district": "A", "social_category": "obc", "is_rural": True, "gender": "male"},
        "c4": {"district": "C", "social_category": "st", "is_rural": False, "gender": "female"},
        "c5": {"district": "B", "social_category": "general", "is_rural": False, "gender": "male"},
    }


class TestFairnessReranker:
    """Tests for the FairnessReranker."""

    def test_basic_rerank(self, sample_scored_candidates, candidate_metadata):
        reranker = FairnessReranker()
        result = reranker.rerank(sample_scored_candidates, candidate_metadata)
        assert len(result) == 5
        assert all(isinstance(r, RerankedCandidate) for r in result)
        assert result[0].rank == 1

    def test_adjustments_bounded(self, sample_scored_candidates, candidate_metadata):
        config = RerankerConfig(max_total_adjustment=0.10)
        reranker = FairnessReranker(config)
        result = reranker.rerank(sample_scored_candidates, candidate_metadata)
        for r in result:
            delta = abs(r.adjusted_score - r.original_score)
            assert delta <= 0.10 + 1e-6

    def test_social_category_boost(self, sample_scored_candidates, candidate_metadata):
        """Test that SC/ST/OBC candidates receive boosts."""
        reranker = FairnessReranker()
        result = reranker.rerank(sample_scored_candidates, candidate_metadata)
        
        # Find c2 (SC) and c3 (OBC) in results
        c2_result = next((r for r in result if r.candidate_id == "c2"), None)
        c3_result = next((r for r in result if r.candidate_id == "c3"), None)
        
        assert c2_result is not None
        assert c3_result is not None
        assert "social_category" in c2_result.adjustments
        assert "social_category" in c3_result.adjustments

    def test_rural_boost(self, sample_scored_candidates, candidate_metadata):
        """Test that rural candidates receive boosts."""
        reranker = FairnessReranker()
        result = reranker.rerank(sample_scored_candidates, candidate_metadata)
        
        # c2 and c3 are rural
        c2_result = next((r for r in result if r.candidate_id == "c2"), None)
        c3_result = next((r for r in result if r.candidate_id == "c3"), None)
        
        assert c2_result is not None
        assert c3_result is not None
        assert "rural" in c2_result.adjustments
        assert "rural" in c3_result.adjustments

    def test_gender_boost(self, sample_scored_candidates, candidate_metadata):
        """Test that female candidates receive boosts."""
        reranker = FairnessReranker()
        result = reranker.rerank(sample_scored_candidates, candidate_metadata)
        
        # c2 and c4 are female
        c2_result = next((r for r in result if r.candidate_id == "c2"), None)
        c4_result = next((r for r in result if r.candidate_id == "c4"), None)
        
        assert c2_result is not None
        assert c4_result is not None
        assert "gender" in c2_result.adjustments
        assert "gender" in c4_result.adjustments

    def test_empty_input(self, candidate_metadata):
        reranker = FairnessReranker()
        result = reranker.rerank([], candidate_metadata)
        assert result == []

    def test_no_change_when_all_disabled(self, sample_scored_candidates, candidate_metadata):
        config = RerankerConfig(
            sc_boost=0.0,
            st_boost=0.0,
            obc_boost=0.0,
            rural_boost=0.0,
            female_boost=0.0,
            underrepresented_district_bonus=0.0,
        )
        reranker = FairnessReranker(config)
        result = reranker.rerank(sample_scored_candidates, candidate_metadata)
        
        for r in result:
            assert r.adjusted_score == r.original_score
            assert len(r.adjustments) == 0

    def test_results_sorted_by_adjusted_score(self, sample_scored_candidates, candidate_metadata):
        reranker = FairnessReranker()
        result = reranker.rerank(sample_scored_candidates, candidate_metadata)
        
        # Verify results are sorted by adjusted_score descending
        scores = [r.adjusted_score for r in result]
        assert scores == sorted(scores, reverse=True)
        
        # Verify ranks are assigned correctly
        for i, r in enumerate(result):
            assert r.rank == i + 1


class TestRerankerConfig:
    """Tests for RerankerConfig."""

    def test_defaults(self):
        config = RerankerConfig()
        assert config.sc_boost == 0.08
        assert config.st_boost == 0.10
        assert config.obc_boost == 0.05
        assert config.rural_boost == 0.06
        assert config.female_boost == 0.03
        assert config.max_total_adjustment == 0.25

    def test_custom_values(self):
        config = RerankerConfig(
            sc_boost=0.15,
            st_boost=0.20,
            max_total_adjustment=0.50,
        )
        assert config.sc_boost == 0.15
        assert config.st_boost == 0.20
        assert config.max_total_adjustment == 0.50
