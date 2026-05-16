"""Fairness-aware re-ranking service with configurable equity policies."""

import logging
from typing import Any

from app.core.config import get_settings
from app.models.candidate import CandidateProfile
from app.models.opportunity import Opportunity

logger = logging.getLogger(__name__)
settings = get_settings()


class FairnessService:
    """Re-ranks match candidates to ensure equitable representation.

    Implements configurable boosts for underrepresented groups
    (social categories SC/ST/OBC/EWS, rural candidates, gender parity).
    """

    def rerank(
        self,
        candidate: CandidateProfile,
        scored: list[tuple[Opportunity, float, dict[str, float]]],
    ) -> list[tuple[Opportunity, float, dict[str, float]]]:
        """Apply fairness-aware re-ranking to scored matches.

        Adjusts scores based on candidate's social category and rural status
        to ensure historically disadvantaged groups receive equitable access.

        Args:
            candidate: The candidate profile.
            scored: List of (opportunity, score, breakdown) tuples sorted by score.

        Returns:
            Re-ranked list with fairness adjustments applied.
        """
        if not scored:
            return scored

        adjusted: list[tuple[Opportunity, float, dict[str, float]]] = []

        for opp, score, breakdown in scored:
            fairness_boost = self._compute_fairness_boost(candidate, opp)
            new_score = min(score + fairness_boost, 1.0)

            adjusted_breakdown = breakdown.copy()
            adjusted_breakdown["fairness_boost"] = fairness_boost
            adjusted_breakdown["original_score"] = score

            adjusted.append((opp, new_score, adjusted_breakdown))

        # Sort by adjusted score
        adjusted.sort(key=lambda x: x[1], reverse=True)

        logger.debug(
            "Fairness re-ranking for candidate %d: max boost=%.3f",
            candidate.id,
            max((a[2].get("fairness_boost", 0) for a in adjusted), default=0),
        )

        return adjusted

    def _compute_fairness_boost(self, candidate: CandidateProfile, opp: Opportunity) -> float:
        """Compute the fairness boost for a candidate-opportunity pair.

        Combines:
        - Social category boost (SC/ST get highest, OBC/EWS moderate)
        - Rural candidate boost
        - First-generation learner boost (if detectable from education)
        """
        boost = 0.0

        # Social category boost
        if candidate.social_category:
            category_boosts = {
                "sc": settings.FAIRNESS_SOCIAL_CATEGORY_BOOST,
                "st": settings.FAIRNESS_SOCIAL_CATEGORY_BOOST,
                "obc": settings.FAIRNESS_SOCIAL_CATEGORY_BOOST * 0.6,
                "ews": settings.FAIRNESS_SOCIAL_CATEGORY_BOOST * 0.5,
                "general": 0.0,
            }
            boost += category_boosts.get(candidate.social_category, 0.0)

        # Rural candidate boost
        if candidate.is_rural:
            boost += settings.FAIRNESS_RURAL_BOOST

        # Location preference for underserved areas
        underserved_states = {
            "bihar",
            "jharkhand",
            "chhattisgarh",
            "odisha",
            "madhya pradesh",
            "rajasthan",
            "uttar pradesh",
        }
        if candidate.state and candidate.state.lower() in underserved_states:
            boost += 0.05

        return round(boost, 4)

    def compute_group_fairness_metrics(
        self,
        allocations: list[dict[str, Any]],
        candidates: dict[int, CandidateProfile],
    ) -> dict[str, Any]:
        """Compute fairness metrics across allocated candidates.

        Returns distribution metrics for audit and reporting.
        """
        if not allocations:
            return {"total": 0}

        category_counts: dict[str, int] = {}
        rural_count = 0
        total = len(allocations)

        for alloc in allocations:
            cand = candidates.get(alloc.get("candidate_id"))
            if cand is None:
                continue
            cat = cand.social_category or "unknown"
            category_counts[cat] = category_counts.get(cat, 0) + 1
            if cand.is_rural:
                rural_count += 1

        return {
            "total": total,
            "category_distribution": category_counts,
            "category_percentages": {k: round(v / total * 100, 1) for k, v in category_counts.items()},
            "rural_count": rural_count,
            "rural_percentage": round(rural_count / total * 100, 1) if total else 0,
        }
