"""
Evaluation Metrics – Ranking Quality Assessment
=================================================

Computes standard information retrieval metrics for evaluating the
quality of the matching/ranking pipeline:

    - NDCG (Normalised Discounted Cumulative Gain)
    - MAP (Mean Average Precision)
    - MRR (Mean Reciprocal Rank)
    - Precision@K
    - Recall@K
    - Hit Rate@K

These metrics are used during model training, A/B testing, and
periodic quality audits.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Aggregated evaluation metrics."""

    ndcg_at_k: dict[int, float] = field(default_factory=dict)
    map_score: float = 0.0
    mrr: float = 0.0
    precision_at_k: dict[int, float] = field(default_factory=dict)
    recall_at_k: dict[int, float] = field(default_factory=dict)
    hit_rate_at_k: dict[int, float] = field(default_factory=dict)
    num_queries: int = 0
    num_relevant_total: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "ndcg_at_k": {f"ndcg@{k}": round(v, 4) for k, v in self.ndcg_at_k.items()},
            "map": round(self.map_score, 4),
            "mrr": round(self.mrr, 4),
            "precision_at_k": {f"p@{k}": round(v, 4) for k, v in self.precision_at_k.items()},
            "recall_at_k": {f"r@{k}": round(v, 4) for k, v in self.recall_at_k.items()},
            "hit_rate_at_k": {f"hr@{k}": round(v, 4) for k, v in self.hit_rate_at_k.items()},
            "num_queries": self.num_queries,
            "num_relevant_total": self.num_relevant_total,
        }

    def summary(self) -> str:
        """One-line summary for logging."""
        ndcg10 = self.ndcg_at_k.get(10, 0)
        return f"NDCG@10={ndcg10:.4f} MAP={self.map_score:.4f} MRR={self.mrr:.4f} queries={self.num_queries}"


class RankingEvaluator:
    """
    Computes ranking quality metrics for the matching pipeline.

    Each "query" is an opportunity, and the "documents" are candidates
    ranked by the pipeline. Relevance labels come from actual allocation
    outcomes or manual annotations.

    Usage:
        evaluator = RankingEvaluator()
        result = evaluator.evaluate(
            ranked_lists=[[("c1", 1.0), ("c2", 0.5), ("c3", 0.0)]],
            relevance_dicts=[{"c1": 3, "c2": 1, "c3": 0}],
        )
    """

    def __init__(self, default_k_values: list[int] | None = None) -> None:
        self._k_values = default_k_values or [1, 3, 5, 10, 20, 50]

    def evaluate(
        self,
        ranked_lists: list[list[tuple[str, float]]],
        relevance_dicts: list[dict[str, float]],
        k_values: list[int] | None = None,
    ) -> EvaluationResult:
        if len(ranked_lists) != len(relevance_dicts):
            raise ValueError("ranked_lists and relevance_dicts must have the same length")

        ks = k_values or self._k_values
        n_queries = len(ranked_lists)

        ndcg_sums: dict[int, float] = {k: 0.0 for k in ks}
        precision_sums: dict[int, float] = {k: 0.0 for k in ks}
        recall_sums: dict[int, float] = {k: 0.0 for k in ks}
        hit_sums: dict[int, float] = {k: 0.0 for k in ks}
        ap_sum = 0.0
        rr_sum = 0.0
        total_relevant = 0

        for ranked, relevance in zip(ranked_lists, relevance_dicts, strict=False):
            ids = [item[0] for item in ranked]
            rels = np.array([relevance.get(cid, 0) for cid in ids])

            for k in ks:
                ndcg_sums[k] += self._ndcg_at_k(rels, k)

            ap_sum += self._average_precision(rels)
            rr_sum += self._reciprocal_rank(rels)

            num_relevant = sum(1 for v in relevance.values() if v > 0)
            total_relevant += num_relevant

            for k in ks:
                top_k_rels = rels[:k]
                precision_sums[k] += float(np.sum(top_k_rels > 0)) / k
                if num_relevant > 0:
                    recall_sums[k] += float(np.sum(top_k_rels > 0)) / num_relevant
                hit_sums[k] += 1.0 if np.any(top_k_rels > 0) else 0.0

        result = EvaluationResult(
            ndcg_at_k={k: ndcg_sums[k] / n_queries for k in ks},
            map_score=ap_sum / n_queries,
            mrr=rr_sum / n_queries,
            precision_at_k={k: precision_sums[k] / n_queries for k in ks},
            recall_at_k={k: recall_sums[k] / n_queries for k in ks},
            hit_rate_at_k={k: hit_sums[k] / n_queries for k in ks},
            num_queries=n_queries,
            num_relevant_total=total_relevant,
        )

        logger.info("Evaluation complete: %s", result.summary())
        return result

    def evaluate_binary(
        self,
        ranked_lists: list[list[str]],
        relevant_sets: list[set[str]],
        k_values: list[int] | None = None,
    ) -> EvaluationResult:
        relevance_dicts = [
            {cid: (1.0 if cid in rel_set else 0.0) for cid in ranked}
            for ranked, rel_set in zip(ranked_lists, relevant_sets, strict=False)
        ]
        ranked_with_scores = [
            [(cid, float(len(ranked) - i)) for i, cid in enumerate(ranked)] for ranked in ranked_lists
        ]
        return self.evaluate(ranked_with_scores, relevance_dicts, k_values)

    @staticmethod
    def _dcg_at_k(relevances: np.ndarray, k: int) -> float:
        k = min(k, len(relevances))
        if k == 0:
            return 0.0
        positions = np.arange(1, k + 1)
        discounts = 1.0 / np.log2(positions + 1)
        gains = 2 ** relevances[:k] - 1
        return float(np.sum(gains * discounts))

    def _ndcg_at_k(self, relevances: np.ndarray, k: int) -> float:
        dcg = self._dcg_at_k(relevances, k)
        ideal = np.sort(relevances)[::-1]
        idcg = self._dcg_at_k(ideal, k)
        if idcg == 0:
            return 0.0
        return dcg / idcg

    @staticmethod
    def _average_precision(relevances: np.ndarray) -> float:
        num_relevant = np.sum(relevances > 0)
        if num_relevant == 0:
            return 0.0
        precisions = []
        for k in range(len(relevances)):
            if relevances[k] > 0:
                prec_at_k = float(np.sum(relevances[: k + 1] > 0)) / (k + 1)
                precisions.append(prec_at_k)
        return float(np.sum(precisions) / num_relevant) if precisions else 0.0

    @staticmethod
    def _reciprocal_rank(relevances: np.ndarray) -> float:
        for i, rel in enumerate(relevances):
            if rel > 0:
                return 1.0 / (i + 1)
        return 0.0

    def cross_validate(
        self,
        all_ranked: list[list[list[tuple[str, float]]]],
        all_relevance: list[list[dict[str, float]]],
        fold_names: list[str] | None = None,
    ) -> dict[str, EvaluationResult]:
        if fold_names is None:
            fold_names = [f"fold_{i}" for i in range(len(all_ranked))]

        results: dict[str, EvaluationResult] = {}
        for name, ranked, relevance in zip(fold_names, all_ranked, all_relevance, strict=False):
            results[name] = self.evaluate(ranked, relevance)
            logger.info("Fold %s: %s", name, results[name].summary())

        all_ndcg10 = [r.ndcg_at_k.get(10, 0) for r in results.values()]
        logger.info(
            "Cross-validation NDCG@10: mean=%.4f, std=%.4f",
            np.mean(all_ndcg10),
            np.std(all_ndcg10),
        )
        return results


# ─── Module-level convenience functions (required by tests) ──────────────────


def ndcg_at_k(
    y_true: np.ndarray,
    y_score: np.ndarray,
    k: int = 10,
) -> float:
    """NDCG@K for a single ranked list."""
    if len(y_true) == 0:
        return 0.0
    order = np.argsort(y_score)[::-1]
    relevances = np.array(y_true, dtype=float)[order]
    evaluator = RankingEvaluator()
    return evaluator._ndcg_at_k(relevances, k)


def mean_average_precision(
    y_true: np.ndarray,
    y_score: np.ndarray,
) -> float:
    """Mean Average Precision for a single query."""
    if len(y_true) == 0:
        return 0.0
    order = np.argsort(y_score)[::-1]
    relevances = np.array(y_true, dtype=float)[order]
    return RankingEvaluator._average_precision(relevances)


def mean_reciprocal_rank(
    y_true: np.ndarray,
    y_score: np.ndarray,
) -> float:
    """Mean Reciprocal Rank for a single query."""
    if len(y_true) == 0:
        return 0.0
    order = np.argsort(y_score)[::-1]
    relevances = np.array(y_true, dtype=float)[order]
    return RankingEvaluator._reciprocal_rank(relevances)
