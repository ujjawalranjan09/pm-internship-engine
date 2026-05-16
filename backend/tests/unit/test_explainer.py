"""Tests for the explainer module."""

import pytest

from app.ml.ranking.explainer import (
    explain_match,
    candidate_facing_explanation,
    admin_facing_explanation,
    score_breakdown,
)


@pytest.fixture
def sample_candidate():
    return {
        "candidate_id": "c1",
        "name": "Priya Sharma",
        "skills": ["python", "machine learning", "data analysis", "sql"],
        "district": "South Delhi",
        "state": "Delhi",
        "education": "B.Tech Computer Science",
        "is_rural": False,
    }


@pytest.fixture
def sample_opportunity():
    return {
        "opportunity_id": "o1",
        "title": "Data Science Intern",
        "organization": "NITI Aayog",
        "location": "New Delhi",
        "required_skills": ["python", "machine learning"],
        "category": "technology",
    }


@pytest.fixture
def sample_scores():
    return {
        "skill_match": 0.85,
        "location_match": 0.90,
        "education_match": 0.70,
        "experience_match": 0.50,
        "semantic_similarity": 0.75,
        "heuristic_score": 0.80,
        "ml_score": 0.72,
    }


class TestExplainMatch:
    """Tests for explain_match function."""

    def test_returns_explanation(self, sample_candidate, sample_opportunity, sample_scores):
        result = explain_match(sample_candidate, sample_opportunity, sample_scores)
        assert result.candidate_id == "c1"
        assert result.opportunity_id == "o1"
        assert 0 < result.final_score <= 1.0

    def test_score_breakdown_populated(self, sample_candidate, sample_opportunity, sample_scores):
        result = explain_match(sample_candidate, sample_opportunity, sample_scores)
        assert len(result.score_breakdown) == len(sample_scores)
        total_pct = sum(b.percentage for b in result.score_breakdown)
        assert total_pct == pytest.approx(100.0, abs=1.0)

    def test_strengths_identified(self, sample_candidate, sample_opportunity, sample_scores):
        result = explain_match(sample_candidate, sample_opportunity, sample_scores)
        assert len(result.strengths) > 0

    def test_candidate_text_not_empty(self, sample_candidate, sample_opportunity, sample_scores):
        result = explain_match(sample_candidate, sample_opportunity, sample_scores)
        assert len(result.candidate_facing) > 50

    def test_admin_text_contains_breakdown(self, sample_candidate, sample_opportunity, sample_scores):
        result = explain_match(sample_candidate, sample_opportunity, sample_scores)
        assert "Score Breakdown" in result.admin_facing
        assert "c1" in result.admin_facing

    def test_with_shap_values(self, sample_candidate, sample_opportunity, sample_scores):
        shap_vals = {"skill_match": 0.3, "location_match": 0.2, "education_match": -0.1}
        result = explain_match(
            sample_candidate, sample_opportunity, sample_scores, shap_values=shap_vals
        )
        assert result.shap_top_features is not None
        assert len(result.shap_top_features) == 3


class TestCandidateFacingExplanation:
    """Tests for candidate_facing_explanation helper."""

    def test_returns_string(self, sample_candidate, sample_opportunity, sample_scores):
        explanation = explain_match(sample_candidate, sample_opportunity, sample_scores)
        text = candidate_facing_explanation(explanation)
        assert isinstance(text, str)
        assert "Priya Sharma" in text


class TestAdminFacingExplanation:
    """Tests for admin_facing_explanation helper."""

    def test_returns_string(self, sample_candidate, sample_opportunity, sample_scores):
        explanation = explain_match(sample_candidate, sample_opportunity, sample_scores)
        text = admin_facing_explanation(explanation)
        assert isinstance(text, str)
        assert "NITI Aayog" in text


class TestScoreBreakdown:
    """Tests for score_breakdown helper."""

    def test_returns_list_of_dicts(self, sample_candidate, sample_opportunity, sample_scores):
        explanation = explain_match(sample_candidate, sample_opportunity, sample_scores)
        breakdown = score_breakdown(explanation)
        assert isinstance(breakdown, list)
        assert all(isinstance(b, dict) for b in breakdown)
        assert all("component_name" in b for b in breakdown)
        assert all("percentage" in b for b in breakdown)
