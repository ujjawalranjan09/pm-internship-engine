"""Tests for the fairness metrics module."""

import numpy as np
import pandas as pd
import pytest

from app.ml.fairness.fairness_metrics import (
    category_distribution,
    concentration_index,
    gini_coefficient,
    geographic_distribution,
    rural_urban_ratio,
    gender_distribution,
    compute_all_fairness_metrics,
)


class TestGiniCoefficient:
    """Tests for gini_coefficient function."""

    def test_perfect_equality(self):
        values = np.array([10, 10, 10, 10])
        assert gini_coefficient(values) == pytest.approx(0.0, abs=1e-6)

    def test_perfect_inequality(self):
        values = np.array([0, 0, 0, 100])
        assert gini_coefficient(values) == pytest.approx(0.75, abs=1e-2)

    def test_empty_array(self):
        assert gini_coefficient(np.array([])) == 0.0

    def test_single_value(self):
        assert gini_coefficient(np.array([50])) == 0.0

    def test_all_zeros(self):
        assert gini_coefficient(np.array([0, 0, 0])) == 0.0

    def test_moderate_inequality(self):
        values = np.array([10, 20, 30, 40])
        gini = gini_coefficient(values)
        assert 0.0 < gini < 1.0

    def test_negative_values_clipped(self):
        values = np.array([-5, 10, 20])
        gini = gini_coefficient(values)
        assert 0.0 <= gini <= 1.0


class TestConcentrationIndex:
    """Tests for concentration_index (HHI)."""

    def test_even_distribution(self):
        opps = {"A": 10, "B": 10, "C": 10, "D": 10}
        hhi = concentration_index(opps)
        assert hhi == pytest.approx(0.0, abs=1e-6)

    def test_full_concentration(self):
        opps = {"A": 100, "B": 0, "C": 0}
        hhi = concentration_index(opps)
        assert hhi == pytest.approx(1.0, abs=1e-6)

    def test_single_region(self):
        opps = {"A": 50}
        assert concentration_index(opps) == 1.0

    def test_empty(self):
        assert concentration_index({}) == 0.0

    def test_moderate_concentration(self):
        opps = {"A": 50, "B": 30, "C": 20}
        hhi = concentration_index(opps)
        assert 0.0 < hhi < 1.0


class TestCategoryDistribution:
    """Tests for category_distribution function."""

    def test_basic_distribution(self):
        candidates = pd.DataFrame({
            "candidate_id": [1, 2, 3, 4, 5],
            "category": ["general", "obc", "sc", "st", "general"],
        })
        allocations = pd.DataFrame({
            "candidate_id": [1, 3, 5],
            "opportunity_id": [10, 10, 11],
        })
        result = category_distribution(allocations, candidates)
        assert "general" in result
        assert "sc" in result
        assert result["general"]["allocated"] == 2
        assert result["sc"]["allocated"] == 1

    def test_no_category_column(self):
        candidates = pd.DataFrame({"candidate_id": [1, 2]})
        allocations = pd.DataFrame({"candidate_id": [1]})
        result = category_distribution(allocations, candidates)
        assert result == {}

    def test_empty_allocations(self):
        candidates = pd.DataFrame({
            "candidate_id": [1, 2],
            "category": ["general", "obc"],
        })
        allocations = pd.DataFrame({"candidate_id": [], "opportunity_id": []})
        result = category_distribution(allocations, candidates)
        assert result["general"]["allocated"] == 0


class TestGeographicDistribution:
    """Tests for geographic_distribution function."""

    def test_basic_geo_distribution(self):
        candidates = pd.DataFrame({
            "candidate_id": [1, 2, 3],
            "district": ["A", "A", "B"],
        })
        allocations = pd.DataFrame({
            "candidate_id": [1, 2],
            "opportunity_id": [10, 10],
        })
        result = geographic_distribution(allocations, candidates)
        assert result["A"]["allocated"] == 2
        assert result["B"]["allocated"] == 0

    def test_no_geo_column(self):
        candidates = pd.DataFrame({"candidate_id": [1]})
        allocations = pd.DataFrame({"candidate_id": [1]})
        result = geographic_distribution(allocations, candidates)
        assert result == {}


class TestRuralUrbanRatio:
    """Tests for rural_urban_ratio function."""

    def test_basic_ratio(self):
        allocations = pd.DataFrame({
            "candidate_id": [1, 2, 3, 4],
            "is_rural": [True, False, True, False],
        })
        result = rural_urban_ratio(allocations)
        assert result["rural_count"] == 2
        assert result["urban_count"] == 2
        assert result["rural_fraction"] == pytest.approx(0.5)

    def test_missing_column(self):
        allocations = pd.DataFrame({"candidate_id": [1]})
        result = rural_urban_ratio(allocations)
        assert "error" in result


class TestGenderDistribution:
    """Tests for gender_distribution function."""

    def test_basic_gender(self):
        candidates = pd.DataFrame({
            "candidate_id": [1, 2, 3],
            "gender": ["male", "female", "female"],
        })
        allocations = pd.DataFrame({"candidate_id": [1, 2]})
        result = gender_distribution(allocations, candidates)
        assert result["male"]["allocated"] == 1
        assert result["female"]["allocated"] == 1

    def test_no_gender_column(self):
        candidates = pd.DataFrame({"candidate_id": [1]})
        allocations = pd.DataFrame({"candidate_id": [1]})
        result = gender_distribution(allocations, candidates)
        assert result == {}


class TestComputeAllFairnessMetrics:
    """Tests for compute_all_fairness_metrics."""

    def test_full_report(self):
        candidates = pd.DataFrame({
            "candidate_id": [1, 2, 3, 4, 5, 6],
            "category": ["general", "obc", "sc", "st", "general", "obc"],
            "district": ["A", "A", "B", "B", "C", "C"],
            "gender": ["male", "female", "male", "female", "male", "female"],
            "is_rural": [False, True, True, False, False, True],
        })
        allocations = pd.DataFrame({
            "candidate_id": [1, 2, 3, 4],
            "opportunity_id": [10, 10, 11, 11],
        })
        report = compute_all_fairness_metrics(allocations, candidates)
        assert report.overall_fairness_score >= 0.0
        assert report.gini_coefficient >= 0.0
        assert isinstance(report.recommendations, list)

    def test_no_candidates(self):
        allocations = pd.DataFrame({
            "candidate_id": [1, 2],
            "opportunity_id": [10, 10],
        })
        report = compute_all_fairness_metrics(allocations, candidates=None)
        assert report.gini_coefficient == 0.0
