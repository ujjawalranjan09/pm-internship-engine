"""Tests for the reranker module."""

import numpy as np
import pandas as pd
import pytest

from app.ml.ranking.reranker import (
    FairnessReranker,
    RerankerConfig,
)


@pytest.fixture
def sample_candidates():
    return pd.DataFrame({
        "candidate_id": ["c1", "c2", "c3", "c4", "c5"],
        "district": ["A", "B", "A", "C", "B"],
        "category": ["general", "sc", "obc", "st", "general"],
        "is_rural": [False, True, True, False, False],
        "gender": ["male", "female", "male", "female", "male"],
        "previous_allocations": [0, 0, 1, 0, 3],
    })


class TestFairnessReranker:
    """Tests for the FairnessReranker."""

    def test_basic_rerank(self, sample_candidates):
        scores = np.array([0.8, 0.7, 0.6, 0.5, 0.9])
        reranker = FairnessReranker()
        result = reranker.rerank(scores, sample_candidates)
        assert len(result.adjusted_scores) == 5
        assert len(result.original_scores) == 5
        assert result.summary["total_candidates"] == 5

    def test_adjustments_bounded(self, sample_candidates):
        scores = np.array([0.8, 0.7, 0.6, 0.5, 0.9])
        config = RerankerConfig(max_total_adjustment=0.10)
        reranker = FairnessReranker(config)
        result = reranker.rerank(scores, sample_candidates)
        deltas = np.abs(result.adjusted_scores - result.original_scores)
        assert all(d <= 0.10 + 1e-6 for d in deltas)

    def test_repeat_penalty_applied(self, sample_candidates):
        scores = np.array([0.8, 0.7, 0.6, 0.5, 0.9])
        config = RerankerConfig(
            enable_district_uplift=False,
            enable_category_balancing=False,
            enable_rural_preference=False,
            enable_female_uplift=False,
            enable_repeat_penalty=True,
        )
        reranker = FairnessReranker(config)
        result = reranker.rerank(scores, sample_candidates)
        # c5 has 3 previous allocations, should be penalized
        assert result.adjusted_scores[4] < scores[4]

    def test_rural_uplift(self, sample_candidates):
        scores = np.array([0.5, 0.5, 0.5, 0.5, 0.5])
        config = RerankerConfig(
            enable_district_uplift=False,
            enable_category_balancing=False,
            enable_rural_preference=True,
            enable_female_uplift=False,
            enable_repeat_penalty=False,
        )
        reranker = FairnessReranker(config)
        result = reranker.rerank(scores, sample_candidates)
        # c2 and c3 are rural
        assert result.adjusted_scores[1] >= scores[1]
        assert result.adjusted_scores[2] >= scores[2]

    def test_adjustment_log_populated(self, sample_candidates):
        scores = np.array([0.8, 0.7, 0.6, 0.5, 0.9])
        reranker = FairnessReranker()
        result = reranker.rerank(scores, sample_candidates)
        assert isinstance(result.adjustment_log, list)

    def test_summary_has_required_keys(self, sample_candidates):
        scores = np.array([0.8, 0.7, 0.6, 0.5, 0.9])
        reranker = FairnessReranker()
        result = reranker.rerank(scores, sample_candidates)
        assert "total_candidates" in result.summary
        assert "total_adjustments" in result.summary
        assert "score_correlation" in result.summary

    def test_no_change_when_disabled(self, sample_candidates):
        scores = np.array([0.8, 0.7, 0.6, 0.5, 0.9])
        config = RerankerConfig(
            enable_district_uplift=False,
            enable_category_balancing=False,
            enable_rural_preference=False,
            enable_female_uplift=False,
            enable_repeat_penalty=False,
        )
        reranker = FairnessReranker(config)
        result = reranker.rerank(scores, sample_candidates)
        np.testing.assert_array_almost_equal(result.adjusted_scores, scores)


class TestGetAdjustmentSummary:
    """Tests for get_adjustment_summary method."""

    def test_returns_dataframe(self, sample_candidates):
        scores = np.array([0.8, 0.7, 0.6, 0.5, 0.9])
        reranker = FairnessReranker()
        reranker.rerank(scores, sample_candidates)
        summary = reranker.get_adjustment_summary()
        assert isinstance(summary, pd.DataFrame)
