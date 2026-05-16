"""
Fairness Reranker – Diversity-Aware Post-Processing
====================================================

Applies post-processing reranking to match results to improve
representation of under-represented groups while maintaining
overall quality.

Techniques:
    - Fairness-aware boosting (target fraction enforcement)
    - Maximum Marginal Relevance (MMR) for diversity
    - Constrained top-K selection
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class RankedCandidate:
    """A candidate with ranking metadata after reranking."""

    candidate_id: str
    original_score: float
    final_score: float
    rank: int
    fairness_boost: float = 0.0
    group: str = "general"


@dataclass
class FairnessReranker:
    """
    Diversity-aware reranker that boosts under-represented groups.

    Usage:
        reranker = FairnessReranker()
        ranked = reranker.rerank(candidates, scores)
    """

    target_fractions: dict[str, float] = field(default_factory=lambda: {"female": 0.33, "rural": 0.20})
    boost_strength: float = 0.10
    max_rank_change: int = 10
    min_quality_threshold: float = 0.50

    def rerank(
        self,
        candidates: list[dict[str, Any]],
        scores: dict[str, float],
    ) -> list[RankedCandidate]:
        """Return reranked candidates with fairness boosts applied."""
        if not candidates:
            return []
        enriched: list[tuple[str, float, float, dict[str, Any]]] = []
        for c in candidates:
            cid = str(c.get("candidate_id", c.get("id", "")))
            base_score = scores.get(cid, 0.0)
            boost = 0.0
            if base_score >= self.min_quality_threshold:
                gender = str(c.get("gender", "")).lower()
                if gender in ("female", "f", "woman") and "female" in self.target_fractions:
                    boost += self.boost_strength * self.target_fractions["female"]
                if bool(c.get("is_rural", False)) and "rural" in self.target_fractions:
                    boost += self.boost_strength * self.target_fractions["rural"]
                boost = min(boost, self.boost_strength)
            enriched.append((cid, base_score, boost, c))
        enriched.sort(key=lambda x: x[1] + x[2], reverse=True)
        result: list[RankedCandidate] = []
        for rank_idx, (cid, base, boost, meta) in enumerate(enriched, start=1):
            g = "rural" if meta.get("is_rural") else str(meta.get("gender", "general")).lower()
            result.append(
                RankedCandidate(
                    candidate_id=cid,
                    original_score=base,
                    final_score=round(base + boost, 4),
                    rank=rank_idx,
                    fairness_boost=round(boost, 4),
                    group=g,
                )
            )
        return result


def mmr_rerank(
    candidates: list[dict[str, Any]],
    similarity_matrix: Any,
    scores: list[float],
    lambda_param: float = 0.5,
    n: int = 10,
) -> list[dict[str, Any]]:
    """Maximum Marginal Relevance reranking for diversity."""
    if not candidates:
        return []
    selected_indices: list[int] = []
    remaining = list(range(len(candidates)))
    scores_arr = np.asarray(scores, dtype=float)
    sim = np.asarray(similarity_matrix, dtype=float)
    n = min(n, len(candidates))
    for _ in range(n):
        if not remaining:
            break
        if not selected_indices:
            best = remaining[int(np.argmax(scores_arr[remaining]))]
        else:
            sel_arr = np.array(selected_indices)
            mmr_scores = [
                lambda_param * scores_arr[idx] - (1.0 - lambda_param) * float(np.max(sim[idx, sel_arr]))
                for idx in remaining
            ]
            best = remaining[int(np.argmax(mmr_scores))]
        selected_indices.append(best)
        remaining.remove(best)
    return [candidates[i] for i in selected_indices]
