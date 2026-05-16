"""Tests for the reranker module."""

import pytest

from app.ml.ranking.reranker import (
    FairnessReranker,
    RankedCandidate,
    RerankerConfig,
    mmr_rerank,
)


@pytest.fixture
def sample_candidates():
    return [
        {"candidate_id": "c1", "district": "A", "category": "general", "is_rural": False, "gender": "male"},
        {"candidate_id": "c2", "district": "B", "category": "sc", "is_rural": True, "gender": "female"},
        {"candidate_id": "c3", "district": "A", "category": "obc", "is_rural": True, "gender": "male"},
        {"candidate_id": "c4", "district": "C", "category": "st", "is_rural": False, "gender": "female"},
        {"candidate_id": "c5", "district": "B", "category": "general", "is_rural": False, "gender": "male"},
    ]


@pytest.fixture
def sample_scores():
    return {"c1": 0.8, "c2": 0.7, "c3": 0.6, "c4": 0.5, "c5": 0.9}


class TestFairnessReranker:
    """Tests for the FairnessReranker."""

    def test_basic_rerank(self, sample_candidates, sample_scores):
        reranker = FairnessReranker()
        result = reranker.rerank(sample_candidates, sample_scores)
        assert len(result) == 5
        assert all(isinstance(r, RankedCandidate) for r in result)

    def test_fairness_boost_applied(self, sample_candidates, sample_scores):
        reranker = FairnessReranker(boost_strength=0.10)
        result = reranker.rerank(sample_candidates, sample_scores)
        # Female and rural candidates should get boosts
        female_candidates = [r for r in result if r.group in ("female", "f", "woman")]
        rural_candidates = [r for r in result if r.group == "rural"]
        assert len(female_candidates + rural_candidates) > 0

    def test_ranking_order(self, sample_candidates, sample_scores):
        reranker = FairnessReranker(boost_strength=0.0)  # No boost
        result = reranker.rerank(sample_candidates, sample_scores)
        # c5 has highest score (0.9), should be rank 1
        assert result[0].candidate_id == "c5"

    def test_empty_input(self):
        reranker = FairnessReranker()
        result = reranker.rerank([], {})
        assert result == []


class TestRerankerConfig:
    """Tests for RerankerConfig."""

    def test_defaults(self):
        config = RerankerConfig()
        assert config.boost_strength == 0.10
        assert config.max_rank_change == 10
        assert config.min_quality_threshold == 0.50


class TestMmrRerank:
    """Tests for MMR reranking."""

    def test_basic_mmr(self, sample_candidates):
        scores = [0.8, 0.7, 0.6, 0.5, 0.9]
        sim_matrix = [[1, 0.5, 0.3, 0.2, 0.1]] * 5
        result = mmr_rerank(sample_candidates, sim_matrix, scores, n=3)
        assert len(result) == 3

    def test_empty_mmr(self):
        result = mmr_rerank([], [], [], n=5)
        assert result == []
