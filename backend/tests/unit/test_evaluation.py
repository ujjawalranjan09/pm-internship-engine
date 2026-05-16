"""Tests for the evaluation module."""

import numpy as np
import pytest

from app.ml.evaluation import (
    ndcg_at_k,
    mean_average_precision,
    mean_reciprocal_rank,
)


class TestNdcgAtK:
    """Tests for ndcg_at_k function."""

    def test_perfect_ranking(self):
        y_true = np.array([3, 2, 1, 0])
        y_score = np.array([3.0, 2.0, 1.0, 0.0])
        assert ndcg_at_k(y_true, y_score, k=4) == pytest.approx(1.0, abs=1e-6)

    def test_inverse_ranking(self):
        y_true = np.array([3, 2, 1, 0])
        y_score = np.array([0.0, 1.0, 2.0, 3.0])
        ndcg = ndcg_at_k(y_true, y_score, k=4)
        assert ndcg < 1.0

    def test_k1(self):
        y_true = np.array([0, 1])
        y_score = np.array([0.5, 0.9])
        assert ndcg_at_k(y_true, y_score, k=1) == pytest.approx(1.0, abs=1e-6)

    def test_all_relevant(self):
        y_true = np.array([1, 1, 1])
        y_score = np.array([0.9, 0.8, 0.7])
        assert ndcg_at_k(y_true, y_score, k=3) == pytest.approx(1.0, abs=1e-6)

    def test_empty(self):
        assert ndcg_at_k(np.array([]), np.array([]), k=5) == 0.0

    def test_single_item(self):
        assert ndcg_at_k(np.array([1]), np.array([0.5]), k=1) == 1.0


class TestMeanAveragePrecision:
    """Tests for mean_average_precision function."""

    def test_perfect_ranking(self):
        y_true = np.array([1, 1, 0, 0])
        y_score = np.array([0.9, 0.8, 0.3, 0.1])
        assert mean_average_precision(y_true, y_score) == pytest.approx(1.0, abs=1e-6)

    def test_worst_ranking(self):
        y_true = np.array([1, 1, 0, 0])
        y_score = np.array([0.1, 0.2, 0.8, 0.9])
        map_score = mean_average_precision(y_true, y_score)
        assert map_score < 0.6

    def test_single_relevant(self):
        y_true = np.array([0, 0, 1])
        y_score = np.array([0.1, 0.2, 0.9])
        assert mean_average_precision(y_true, y_score) == pytest.approx(1.0, abs=1e-6)

    def test_no_relevant(self):
        y_true = np.array([0, 0, 0])
        y_score = np.array([0.9, 0.8, 0.7])
        assert mean_average_precision(y_true, y_score) == 0.0

    def test_empty(self):
        assert mean_average_precision(np.array([]), np.array([])) == 0.0


class TestMeanReciprocalRank:
    """Tests for mean_reciprocal_rank function."""

    def test_relevant_at_top(self):
        y_true = np.array([1, 0, 0])
        y_score = np.array([0.9, 0.5, 0.1])
        assert mean_reciprocal_rank(y_true, y_score) == pytest.approx(1.0, abs=1e-6)

    def test_relevant_at_second(self):
        y_true = np.array([0, 1, 0])
        y_score = np.array([0.9, 0.8, 0.1])
        assert mean_reciprocal_rank(y_true, y_score) == pytest.approx(0.5, abs=1e-6)

    def test_no_relevant(self):
        y_true = np.array([0, 0, 0])
        y_score = np.array([0.9, 0.8, 0.7])
        assert mean_reciprocal_rank(y_true, y_score) == 0.0

    def test_multiple_relevant(self):
        y_true = np.array([1, 1, 0])
        y_score = np.array([0.5, 0.9, 0.1])
        # First relevant at rank 2 (score 0.9 is rank 1)
        mrr = mean_reciprocal_rank(y_true, y_score)
        assert mrr == pytest.approx(1.0, abs=1e-6)
