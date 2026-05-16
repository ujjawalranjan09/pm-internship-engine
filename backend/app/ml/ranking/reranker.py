"""
Re-Ranker – Fairness-Aware Post-Processing (Stage C)
=====================================================

Adjusts the scores produced by the heuristic and ML rankers to
enforce fairness constraints without sacrificing too much quality.

Strategy:
    1. Apply social-category boosts (SC/ST/OBC uplift)
    2. Apply rural candidate boost
    3. Apply geographic diversity bonus
    4. Enforce minimum representation quotas
    5. Clamp maximum score adjustments to preserve ranking quality
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class RerankerConfig:
    """Configuration for the fairness-aware re-ranker."""

    # Category boosts (additive to score)
    sc_boost: float = 0.08
    st_boost: float = 0.10
    obc_boost: float = 0.05
    general_boost: float = 0.0

    # Rural boost
    rural_boost: float = 0.06

    # Geographic diversity
    underrepresented_district_bonus: float = 0.04
    district_threshold_percentile: float = 0.25  # Bottom 25% get the bonus

    # Quality floor – never boost a candidate below this original score
    min_quality_score: float = 0.20

    # Maximum total adjustment (prevents runaway boosts)
    max_total_adjustment: float = 0.25

    # Gender parity
    female_boost: float = 0.03
    gender_parity_target: float = 0.40  # Target 40% female representation

    # Feature flags for FairnessReranker
    enable_district_uplift: bool = True
    enable_category_balancing: bool = True
    enable_rural_preference: bool = True
    enable_female_uplift: bool = True
    enable_repeat_penalty: bool = True


@dataclass
class RerankedCandidate:
    """A candidate after fairness-aware re-ranking."""

    candidate_id: str
    opportunity_id: str
    original_score: float
    adjusted_score: float
    adjustments: dict[str, float] = field(default_factory=dict)
    rank: int = 0


class Reranker:
    """
    Fairness-aware re-ranker.

    Takes the output of the heuristic/ML scorers and applies fairness
    adjustments to promote equitable representation while preserving
    overall match quality.

    Usage:
        reranker = Reranker(config)
        results = reranker.rerank(scored_candidates, candidate_metadata)
    """

    def __init__(self, config: RerankerConfig | None = None) -> None:
        self.config = config or RerankerConfig()

    def rerank(
        self,
        scored: list[dict[str, Any]],
        candidate_metadata: dict[str, dict[str, Any]],
        opportunity_metadata: dict[str, Any] | None = None,
        district_counts: dict[str, int] | None = None,
    ) -> list[RerankedCandidate]:
        """
        Re-rank scored candidates with fairness adjustments.

        Args:
            scored: List of dicts with keys:
                candidate_id, opportunity_id, score, rank
            candidate_metadata: Dict mapping candidate_id to metadata:
                social_category, is_rural, district, gender (optional)
            opportunity_metadata: Opportunity context (optional).
            district_counts: Current allocation counts per district
                (for diversity bonus). If None, no district bonus applied.

        Returns:
            List of RerankedCandidate sorted by adjusted_score descending.
        """
        if not scored:
            return []

        # Determine under-represented districts
        underrepresented: set = set()
        if district_counts and district_counts:
            values = list(district_counts.values())
            if values:
                threshold = np.percentile(values, self.config.district_threshold_percentile * 100)
                underrepresented = {d for d, c in district_counts.items() if c <= threshold}

        results: list[RerankedCandidate] = []

        for item in scored:
            cid = str(item["candidate_id"])
            oid = str(item["opportunity_id"])
            original = float(item["score"])
            meta = candidate_metadata.get(cid, {})

            adjustments: dict[str, float] = {}

            # Skip candidates below quality floor
            if original < self.config.min_quality_score:
                results.append(
                    RerankedCandidate(
                        candidate_id=cid,
                        opportunity_id=oid,
                        original_score=original,
                        adjusted_score=original,
                        adjustments={},
                    )
                )
                continue

            # Social category boost
            category = (meta.get("social_category") or "general").lower()
            category_boost = {
                "sc": self.config.sc_boost,
                "scheduled caste": self.config.sc_boost,
                "st": self.config.st_boost,
                "scheduled tribe": self.config.st_boost,
                "obc": self.config.obc_boost,
                "other backward class": self.config.obc_boost,
            }.get(category, self.config.general_boost)

            if category_boost > 0:
                adjustments["social_category"] = category_boost

            # Rural boost
            if meta.get("is_rural", False):
                adjustments["rural"] = self.config.rural_boost

            # Gender boost
            gender = (meta.get("gender") or "").lower()
            if gender in ("female", "f", "woman"):
                adjustments["gender"] = self.config.female_boost

            # District diversity bonus
            district = meta.get("district")
            if district and district in underrepresented:
                adjustments["district_diversity"] = self.config.underrepresented_district_bonus

            # Clamp total adjustment
            total_adjustment = sum(adjustments.values())
            if total_adjustment > self.config.max_total_adjustment:
                scale = self.config.max_total_adjustment / total_adjustment
                adjustments = {k: v * scale for k, v in adjustments.items()}
                total_adjustment = self.config.max_total_adjustment

            adjusted = min(1.0, original + total_adjustment)

            results.append(
                RerankedCandidate(
                    candidate_id=cid,
                    opportunity_id=oid,
                    original_score=original,
                    adjusted_score=adjusted,
                    adjustments=adjustments,
                )
            )

        # Sort by adjusted score descending
        results.sort(key=lambda r: -r.adjusted_score)
        for i, r in enumerate(results):
            r.rank = i + 1

        return results

    def rerank_with_quota(
        self,
        scored: list[dict[str, Any]],
        candidate_metadata: dict[str, dict[str, Any]],
        quotas: dict[str, float],
        total_slots: int,
    ) -> list[RerankedCandidate]:
        """
        Re-rank with hard minimum representation quotas.

        Ensures that at least `quota_fraction * total_slots` candidates
        from each quota group are in the top results.

        Args:
            scored: Scored candidates.
            candidate_metadata: Candidate metadata.
            quotas: Dict mapping category name to minimum fraction.
                e.g. {"sc": 0.15, "st": 0.075, "obc": 0.27}
            total_slots: Total number of allocation slots.

        Returns:
            Re-ranked candidates with quota guarantees.
        """
        # First pass: normal rerank
        reranked = self.rerank(scored, candidate_metadata)

        if not quotas or total_slots <= 0:
            return reranked

        # Calculate required counts per group
        required: dict[str, int] = {}
        for group, fraction in quotas.items():
            required[group.lower()] = max(1, int(fraction * total_slots))

        # Check if quotas are already met in top results
        top = reranked[:total_slots]
        group_counts: dict[str, int] = {}
        for r in top:
            meta = candidate_metadata.get(r.candidate_id, {})
            cat = (meta.get("social_category") or "general").lower()
            group_counts[cat] = group_counts.get(cat, 0) + 1

        # If all quotas met, return as-is
        all_met = all(group_counts.get(group, 0) >= count for group, count in required.items())
        if all_met:
            return reranked

        # Quota enforcement: swap in under-represented candidates
        # from below the cutoff
        result_ids = {r.candidate_id for r in top}
        remaining = [r for r in reranked[total_slots:] if r.candidate_id not in result_ids]

        for group, needed in required.items():
            current = group_counts.get(group, 0)
            if current >= needed:
                continue

            # Find candidates from this group in remaining
            group_remaining = [
                r
                for r in remaining
                if (candidate_metadata.get(r.candidate_id, {}).get("social_category", "general").lower() == group)
            ]

            # Swap in the highest-scoring ones
            swaps_needed = needed - current
            for candidate in group_remaining[:swaps_needed]:
                # Replace the lowest-scoring non-quota candidate in top
                for j in range(len(top) - 1, -1, -1):
                    meta_j = candidate_metadata.get(top[j].candidate_id, {})
                    cat_j = (meta_j.get("social_category") or "general").lower()
                    if cat_j not in required or group_counts.get(cat_j, 0) > required.get(cat_j, 0):
                        group_counts[cat_j] = group_counts.get(cat_j, 0) - 1
                        top[j] = candidate
                        group_counts[group] = group_counts.get(group, 0) + 1
                        remaining.remove(candidate)
                        break

        # Re-sort and re-rank
        top.sort(key=lambda r: -r.adjusted_score)
        for i, r in enumerate(top):
            r.rank = i + 1

        return top + remaining


@dataclass
class RerankResult:
    """Result of a fairness-aware re-ranking operation."""

    original_scores: np.ndarray
    adjusted_scores: np.ndarray
    adjustments: dict[str, np.ndarray] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)
    adjustment_log: list[dict[str, Any]] = field(default_factory=list)


class FairnessReranker:
    """
    Fairness-aware re-ranker with configurable adjustments.
    
    This is an alternative implementation that works with numpy arrays
    and pandas DataFrames for easier integration with test suites.
    """

    def __init__(self, config: RerankerConfig | None = None) -> None:
        self.config = config or RerankerConfig()
        self._adjustment_log: list[dict[str, Any]] = []

    def rerank(
        self,
        scores: np.ndarray,
        candidates: Any,  # pandas DataFrame
        opportunity_id: str = "default",
    ) -> RerankResult:
        """
        Re-rank candidates with fairness adjustments.
        
        Args:
            scores: Original scores as numpy array.
            candidates: pandas DataFrame with columns:
                candidate_id, district, category, is_rural, gender, previous_allocations
            opportunity_id: Optional opportunity ID for logging.
            
        Returns:
            RerankResult with original and adjusted scores.
        """
        import pandas as pd
        
        n = len(scores)
        adjusted = scores.copy()
        adjustments: dict[str, np.ndarray] = {}
        self._adjustment_log = []
        
        # Enable flags
        enable_district = getattr(self.config, "enable_district_uplift", True)
        enable_category = getattr(self.config, "enable_category_balancing", True)
        enable_rural = getattr(self.config, "enable_rural_preference", True)
        enable_female = getattr(self.config, "enable_female_uplift", True)
        enable_repeat = getattr(self.config, "enable_repeat_penalty", True)
        
        # Category boosts
        if enable_category and "category" in candidates.columns:
            cat_boost = np.zeros(n)
            for i, row in candidates.iterrows():
                cat = (row.get("category") or "general").lower()
                if cat in ("sc", "scheduled caste"):
                    cat_boost[i] = self.config.sc_boost
                elif cat in ("st", "scheduled tribe"):
                    cat_boost[i] = self.config.st_boost
                elif cat in ("obc", "other backward class"):
                    cat_boost[i] = self.config.obc_boost
            if np.any(cat_boost > 0):
                adjustments["category"] = cat_boost
                adjusted += cat_boost
                self._adjustment_log.append({"type": "category", "boost": cat_boost.tolist()})
        
        # Rural boost
        if enable_rural and "is_rural" in candidates.columns:
            rural_mask = candidates["is_rural"].astype(bool).values
            rural_boost = np.where(rural_mask, self.config.rural_boost, 0.0)
            if np.any(rural_boost > 0):
                adjustments["rural"] = rural_boost
                adjusted += rural_boost
                self._adjustment_log.append({"type": "rural", "boost": rural_boost.tolist()})
        
        # Female boost
        if enable_female and "gender" in candidates.columns:
            female_mask = candidates["gender"].apply(lambda x: str(x).lower() in ("f", "female", "woman")).values
            female_boost = np.where(female_mask, self.config.female_boost, 0.0)
            if np.any(female_boost > 0):
                adjustments["gender"] = female_boost
                adjusted += female_boost
                self._adjustment_log.append({"type": "gender", "boost": female_boost.tolist()})
        
        # Repeat penalty
        if enable_repeat and "previous_allocations" in candidates.columns:
            prev = candidates["previous_allocations"].values.astype(float)
            repeat_penalty = -0.05 * np.minimum(prev, 3)  # Cap at 3 previous allocations
            if np.any(repeat_penalty < 0):
                adjustments["repeat_penalty"] = repeat_penalty
                adjusted += repeat_penalty
                self._adjustment_log.append({"type": "repeat_penalty", "penalty": repeat_penalty.tolist()})
        
        # Clamp total adjustment
        deltas = adjusted - scores
        abs_deltas = np.abs(deltas)
        needs_clamping = abs_deltas > self.config.max_total_adjustment
        if np.any(needs_clamping):
            scale = self.config.max_total_adjustment / np.maximum(abs_deltas, 1e-9)
            scale = np.minimum(scale, 1.0)
            adjusted = scores + deltas * scale
        
        # Clamp to [0, 1]
        adjusted = np.clip(adjusted, 0.0, 1.0)
        
        # Build summary
        summary = {
            "total_candidates": n,
            "total_adjustments": len(adjustments),
            "score_correlation": float(np.corrcoef(scores, adjusted)[0, 1]) if n > 1 else 1.0,
        }
        
        return RerankResult(
            original_scores=scores,
            adjusted_scores=adjusted,
            adjustments=adjustments,
            summary=summary,
            adjustment_log=self._adjustment_log,
        )

    def get_adjustment_summary(self) -> Any:
        """Return adjustment summary as a pandas DataFrame."""
        import pandas as pd
        
        if not self._adjustment_log:
            return pd.DataFrame()
        
        return pd.DataFrame(self._adjustment_log)
