"""Tests for the fairness guardrails module."""

import numpy as np
import pytest

from app.ml.fairness.guardrails import (
    detect_overcorrection,
    enforce_max_adjustment,
    enforce_min_quality_threshold,
)


class TestEnforceMinQualityThreshold:
    """Tests for enforce_min_quality_threshold."""

    def test_no_change_needed(self):
        original = np.array([0.8, 0.7, 0.9])
        adjusted = np.array([0.75, 0.65, 0.85])
        result = enforce_min_quality_threshold(original, adjusted, threshold=0.6)
        # All adjusted values are above 60% of original
        np.testing.assert_array_almost_equal(result, adjusted)

    def test_clamp_low_values(self):
        original = np.array([0.8, 0.7, 0.9])
        adjusted = np.array([0.3, 0.2, 0.85])  # 0.3 < 0.6*0.8=0.48, 0.2 < 0.6*0.7=0.42
        result = enforce_min_quality_threshold(original, adjusted, threshold=0.6)
        assert result[0] == pytest.approx(0.48, abs=1e-6)  # 0.6 * 0.8
        assert result[1] == pytest.approx(0.42, abs=1e-6)  # 0.6 * 0.7
        assert result[2] == pytest.approx(0.85, abs=1e-6)  # unchanged

    def test_zero_original(self):
        original = np.array([0.0, 0.5])
        adjusted = np.array([0.0, 0.1])
        result = enforce_min_quality_threshold(original, adjusted, threshold=0.6)
        assert result[0] == 0.0
        assert result[1] == pytest.approx(0.3, abs=1e-6)


class TestEnforceMaxAdjustment:
    """Tests for enforce_max_adjustment."""

    def test_no_change_needed(self):
        original = np.array([0.5, 0.6, 0.7])
        adjusted = np.array([0.52, 0.58, 0.71])
        result = enforce_max_adjustment(original, adjusted, max_delta=0.15)
        np.testing.assert_array_almost_equal(result, adjusted)

    def test_clamp_positive(self):
        original = np.array([0.5])
        adjusted = np.array([0.8])  # delta = 0.3 > 0.15
        result = enforce_max_adjustment(original, adjusted, max_delta=0.15)
        assert result[0] == pytest.approx(0.65, abs=1e-6)

    def test_clamp_negative(self):
        original = np.array([0.7])
        adjusted = np.array([0.3])  # delta = -0.4 < -0.15
        result = enforce_max_adjustment(original, adjusted, max_delta=0.15)
        assert result[0] == pytest.approx(0.55, abs=1e-6)

    def test_exact_limit(self):
        original = np.array([0.5])
        adjusted = np.array([0.65])  # delta = 0.15 == max_delta
        result = enforce_max_adjustment(original, adjusted, max_delta=0.15)
        assert result[0] == pytest.approx(0.65, abs=1e-6)


class TestDetectOvercorrection:
    """Tests for detect_overcorrection."""

    def test_no_overcorrection(self):
        before = np.array([0.5, 0.6, 0.4, 0.7])
        after = np.array([0.52, 0.58, 0.42, 0.68])
        group = np.array([True, False, True, False])
        result = detect_overcorrection(before, after, group)
        assert result["is_overcorrected"] is False

    def test_overcorrection_detected(self):
        before = np.array([0.5, 0.6, 0.4, 0.7])
        after = np.array([0.9, 0.6, 0.9, 0.7])  # Massive boost to group=True
        group = np.array([True, False, True, False])
        result = detect_overcorrection(before, after, group)
        assert result["is_overcorrected"] is True
        assert result["group_mean_delta"] > result["non_group_mean_delta"]

    def test_empty_arrays(self):
        result = detect_overcorrection(np.array([]), np.array([]), np.array([]))
        assert result["is_overcorrected"] is False
