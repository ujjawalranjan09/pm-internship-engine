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
        """
        Evaluate ranking quality across multiple queries.

        Args:
            ranked_lists: Per-query ranked results. Each is a list of
                (candidate_id, score) sorted by score descending.
            relevance_dicts: Per-query relevance labels. Each maps
                candidate_id to relevance (0=irrelevant, higher=more relevant).
            k_values: K values for @K metrics. Uses defaults if None.

        Returns:
            EvaluationResult with all metrics.
        """
        if len(ranked_lists) != len(relevance_dicts):
            raise ValueError("ranked_lists and relevance_dicts must have the same length")

        ks = k_values or self._k_values
        n_queries = len(ranked_lists)

        ndcg_sums = {k: 0.0 for k in ks}
        precision_sums = {k: 0.0 for k in ks}
        recall_sums = {k: 0.0 for k in ks}
        hit_sums = {k: 0.0 for k in ks}
        ap_sum = 0.0
        rr_sum = 0.0
        total_relevant = 0

        for ranked, relevance in zip(ranked_lists, relevance_dicts, strict=False):
            ids = [item[0] for item in ranked]
            rels = np.array([relevance.get(cid, 0) for cid in ids])

            # NDCG@K
            for k in ks:
                ndcg_sums[k] += self._ndcg_at_k(rels, k)

            # MAP
            ap_sum += self._average_precision(rels)

            # MRR
            rr_sum += self._reciprocal_rank(rels)

            # Precision, Recall, Hit Rate @K
            num_relevant = sum(1 for v in relevance.values() if v > 0)
            total_relevant += num_relevant

            for k in ks:
                top_k_rels = rels[:k]
                precision_sums[k] += np.sum(top_k_rels > 0) / k
                if num_relevant > 0:
                    recall_sums[k] += np.sum(top_k_rels > 0) / num_relevant
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
        relevant_sets: list[set],
        k_values: list[int] | None = None,
    ) -> EvaluationResult:
        """
        Simplified evaluation with binary relevance (relevant/not).

        Args:
            ranked_lists: Per-query ranked candidate IDs.
            relevant_sets: Per-query set of relevant candidate IDs.

        Returns:
            EvaluationResult.
        """
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
        """
        Compute Discounted Cumulative Gain at K.

        DCG@K = Σ (2^rel_i - 1) / log2(i + 2) for i in [0, K)
        """
        k = min(k, len(relevances))
        if k == 0:
            return 0.0

        positions = np.arange(1, k + 1)
        discounts = 1.0 / np.log2(positions + 1)
        gains = 2 ** relevances[:k] - 1

        return float(np.sum(gains * discounts))

    def _ndcg_at_k(self, relevances: np.ndarray, k: int) -> float:
        """
        Compute Normalised DCG at K.

        NDCG@K = DCG@K / IDCG@K
        """
        dcg = self._dcg_at_k(relevances, k)

        # Ideal ranking: sort by relevance descending
        ideal = np.sort(relevances)[::-1]
        idcg = self._dcg_at_k(ideal, k)

        if idcg == 0:
            return 0.0

        return dcg / idcg

    @staticmethod
    def _average_precision(relevances: np.ndarray) -> float:
        """
        Compute Average Precision for a single query.

        AP = (1/R) × Σ P(k) × rel(k)
        where R = total relevant, P(k) = precision at rank k.
        """
        num_relevant = np.sum(relevances > 0)
        if num_relevant == 0:
            return 0.0

        precisions = []
        for k in range(len(relevances)):
            if relevances[k] > 0:
                prec_at_k = np.sum(relevances[: k + 1] > 0) / (k + 1)
                precisions.append(prec_at_k)

        return float(np.sum(precisions) / num_relevant) if precisions else 0.0

    @staticmethod
    def _reciprocal_rank(relevances: np.ndarray) -> float:
        """
        Compute Reciprocal Rank.

        RR = 1/rank of first relevant item.
        """
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
        """
        Evaluate across multiple folds (e.g. time-based splits).

        Args:
            all_ranked: List of fold → query → ranked results.
            all_relevance: List of fold → query → relevance labels.

        Returns:
            Dict mapping fold name to EvaluationResult.
        """
        if fold_names is None:
            fold_names = [f"fold_{i}" for i in range(len(all_ranked))]

        results = {}
        for name, ranked, relevance in zip(fold_names, all_ranked, all_relevance, strict=False):
            results[name] = self.evaluate(ranked, relevance)
            logger.info("Fold %s: %s", name, results[name].summary())

        # Compute overall stats
        all_ndcg10 = [r.ndcg_at_k.get(10, 0) for r in results.values()]
        logger.info(
            "Cross-validation NDCG@10: mean=%.4f, std=%.4f",
            np.mean(all_ndcg10),
            np.std(all_ndcg10),
        )

        return results
