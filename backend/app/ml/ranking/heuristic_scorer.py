"""
Heuristic Scorer - Fast Rule-Based Ranking (Stage A)
======================================================

Provides a fast, interpretable scoring function for candidate-opportunity
pairs. This is the first ranking stage that produces a baseline score
before ML-based refinement.

Weighted Scoring Formula:
    score = Σ (w_i × feature_i) for all features

Default weights (sum to 1.0):
    skill_match          = 0.30  (highest - skills are primary signal)
    qualification_fit    = 0.15
    sector_interest      = 0.10
    location_preference  = 0.10
    profile_readiness    = 0.10
    employer_preference  = 0.10
    historical_adjustment = 0.05
    semantic_similarity  = 0.10
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from app.ml.feature_engineering.feature_extractor import FeatureVector

logger = logging.getLogger(__name__)


@dataclass
class HeuristicWeights:
    """
    Configurable weights for the heuristic scoring formula.

    All weights should sum to 1.0 for normalized interpretation,
    though the scorer will work with any weights and normalize internally.
    """
    skill_match: float = 0.30
    qualification_fit: float = 0.15
    sector_interest: float = 0.10
    location_preference: float = 0.10
    profile_readiness: float = 0.10
    employer_preference: float = 0.10
    historical_adjustment: float = 0.05
    semantic_similarity: float = 0.10

    def to_array(self) -> np.ndarray:
        """Convert weights to numpy array matching feature order."""
        return np.array([
            self.skill_match,
            self.skill_match,
            self.qualification_fit,
            self.location_preference,
            self.sector_interest,
            self.profile_readiness,
            0.0,
            self.historical_adjustment,
            0.0,
            self.qualification_fit,
            0.0,
            self.semantic_similarity,
            self.skill_match,
        ], dtype=np.float64)

    def normalize(self) -> HeuristicWeights:
        """Return a normalized copy where weights sum to 1.0."""
        arr = self.to_array()
        total = arr.sum()
        if total == 0:
            return HeuristicWeights()

        normalized = arr / total
        return HeuristicWeights(
            skill_match=float(normalized[0]),
            qualification_fit=float(normalized[2]),
            sector_interest=float(normalized[4]),
            location_preference=float(normalized[3]),
            profile_readiness=float(normalized[5]),
            employer_preference=self.employer_preference / total,
            historical_adjustment=float(normalized[7]),
            semantic_similarity=float(normalized[11]),
        )


@dataclass
class ScoredCandidate:
    """A candidate with their computed heuristic score."""
    candidate_id: str
    opportunity_id: str
    score: float
    raw_features: Dict[str, float] = field(default_factory=dict)
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    rank: int = 0


class HeuristicScorer:
    """
    Fast heuristic scoring for candidate-opportunity pairs.

    Computes a weighted combination of features to produce an
    interpretable match score. Designed to be fast enough for
    real-time scoring while providing reasonable ranking quality.
    """

    def __init__(
        self,
        weights: Optional[HeuristicWeights] = None,
        normalize_weights: bool = True,
    ) -> None:
        self.weights = weights or HeuristicWeights()
        if normalize_weights:
            self.weights = self.weights.normalize()

        self._weight_array = self.weights.to_array()

        logger.info(
            "HeuristicScorer initialized with weights: "
            "skill=%.2f, qual=%.2f, sector=%.2f, location=%.2f, "
            "profile=%.2f, employer=%.2f, history=%.2f, semantic=%.2f",
            self.weights.skill_match, self.weights.qualification_fit,
            self.weights.sector_interest, self.weights.location_preference,
            self.weights.profile_readiness, self.weights.employer_preference,
            self.weights.historical_adjustment, self.weights.semantic_similarity,
        )

    def score(self, features: FeatureVector) -> Tuple[float, Dict[str, float]]:
        """Score a single candidate-opportunity pair."""
        feat_array = features.to_array()

        raw_score = float(np.dot(self._weight_array, feat_array))

        competitiveness_bonus = features.competitiveness_percentile * 0.05
        raw_score += competitiveness_bonus

        employer_boost = self.weights.employer_preference * 0.1
        raw_score += employer_boost

        score = self._sigmoid_normalize(raw_score)
        breakdown = self._build_breakdown(features, feat_array)

        return score, breakdown

    def _sigmoid_normalize(self, x: float, temperature: float = 2.0) -> float:
        """Apply sigmoid normalization to score."""
        return 1.0 / (1.0 + math.exp(-temperature * (x - 0.5)))

    def _build_breakdown(
        self, features: FeatureVector, feat_array: np.ndarray
    ) -> Dict[str, float]:
        """Build detailed score breakdown for explainability."""
        feature_names = FeatureVector.feature_names()
        breakdown = {}

        for name, value, weight in zip(feature_names, feat_array, self._weight_array):
            breakdown[name] = {
                "value": float(value),
                "weight": float(weight),
                "contribution": float(value * weight),
            }

        breakdown["_total_raw"] = float(np.dot(self._weight_array, feat_array))
        return breakdown

    def score_batch(self, features_matrix: np.ndarray) -> np.ndarray:
        """Score a batch of feature vectors."""
        raw_scores = features_matrix @ self._weight_array
        scores = 1.0 / (1.0 + np.exp(-2.0 * (raw_scores - 0.5)))
        return np.clip(scores, 0.0, 1.0)

    def rank_candidates(
        self,
        features_matrix: np.ndarray,
        candidate_ids: List[str],
        opportunity_id: str,
        top_k: Optional[int] = None,
        min_score: float = 0.0,
    ) -> List[ScoredCandidate]:
        """Rank candidates for a single opportunity."""
        scores = self.score_batch(features_matrix)

        scored = []
        feature_names = FeatureVector.feature_names()
        for i, (cid, score) in enumerate(zip(candidate_ids, scores)):
            if score >= min_score:
                raw_features = dict(zip(feature_names, features_matrix[i].tolist()))
                scored.append(ScoredCandidate(
                    candidate_id=cid,
                    opportunity_id=opportunity_id,
                    score=float(score),
                    raw_features=raw_features,
                ))

        scored.sort(key=lambda x: -x.score)

        for i, sc in enumerate(scored):
            sc.rank = i + 1

        if top_k is not None:
            scored = scored[:top_k]

        return scored

    def rank_opportunities(
        self,
        features_matrix: np.ndarray,
        candidate_id: str,
        opportunity_ids: List[str],
        top_k: Optional[int] = None,
        min_score: float = 0.0,
    ) -> List[ScoredCandidate]:
        """Rank opportunities for a single candidate."""
        scores = self.score_batch(features_matrix)

        scored = []
        feature_names = FeatureVector.feature_names()
        for i, (oid, score) in enumerate(zip(opportunity_ids, scores)):
            if score >= min_score:
                raw_features = dict(zip(feature_names, features_matrix[i].tolist()))
                scored.append(ScoredCandidate(
                    candidate_id=candidate_id,
                    opportunity_id=oid,
                    score=float(score),
                    raw_features=raw_features,
                ))

        scored.sort(key=lambda x: -x.score)
        for i, sc in enumerate(scored):
            sc.rank = i + 1

        if top_k is not None:
            scored = scored[:top_k]

        return scored

    def update_weights(self, new_weights: Dict[str, float]) -> None:
        """Update scoring weights dynamically."""
        for name, value in new_weights.items():
            if hasattr(self.weights, name):
                setattr(self.weights, name, value)
            else:
                logger.warning("Unknown weight: %s", name)

        self.weights = self.weights.normalize()
        self._weight_array = self.weights.to_array()
        logger.info("Weights updated: %s", new_weights)
