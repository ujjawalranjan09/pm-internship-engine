"""
Model evaluation metrics for ranking quality and fairness assessment.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class RankingMetrics:
    """Ranking quality metrics."""
    ndcg_at_5: float = 0.0
    ndcg_at_10: float = 0.0
    ndcg_at_20: float = 0.0
    map_score: float = 0.0
    mrr: float = 0.0
    precision_at_5: float = 0.0
    precision_at_10: float = 0.0
    recall_at_10: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "ndcg@5": self.ndcg_at_5,
            "ndcg@10": self.ndcg_at_10,
            "ndcg@20": self.ndcg_at_20,
            "map": self.map_score,
            "mrr": self.mrr,
            "precision@5": self.precision_at_5,
            "precision@10": self.precision_at_10,
            "recall@10": self.recall_at_10,
        }


@dataclass
class FairnessReport:
    """Fairness evaluation report."""
    category_distribution: dict[str, float] = field(default_factory=dict)
    geographic_distribution: dict[str, float] = field(default_factory=dict)
    rural_urban_ratio: dict[str, float] = field(default_factory=dict)
    gini_coefficient: float = 0.0
    concentration_index: float = 0.0
    group_parities: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "category_distribution": self.category_distribution,
            "geographic_distribution": self.geographic_distribution,
            "rural_urban_ratio": self.rural_urban_ratio,
            "gini_coefficient": self.gini_coefficient,
            "concentration_index": self.concentration_index,
            "group_parities": self.group_parities,
        }


@dataclass
class EvalReport:
    """Complete evaluation report combining ranking and fairness."""
    ranking: RankingMetrics
    fairness: FairnessReport
    n_samples: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ranking": self.ranking.to_dict(),
            "fairness": self.fairness.to_dict(),
            "n_samples": self.n_samples,
            "metadata": self.metadata,
        }


def ndcg_at_k(y_true: np.ndarray, y_score: np.ndarray, k: int = 10) -> float:
    """
    Compute Normalized Discounted Cumulative Gain at K.

    NDCG measures ranking quality by rewarding relevant items placed higher.

    Args:
        y_true: Relevance labels (higher = more relevant)
        y_score: Predicted scores
        k: Cutoff position

    Returns:
        NDCG score between 0 and 1
    """
    order = np.argsort(y_score)[::-1][:k]
    y_true_sorted = np.take(y_true, order)

    # DCG
    gains = 2 ** y_true_sorted - 1
    discounts = np.log2(np.arange(2, k + 2))
    dcg = np.sum(gains / discounts)

    # Ideal DCG
    ideal_order = np.argsort(y_true)[::-1][:k]
    ideal_gains = 2 ** np.take(y_true, ideal_order) - 1
    idcg = np.sum(ideal_gains / discounts)

    if idcg == 0:
        return 0.0
    return float(dcg / idcg)


def mean_average_precision(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """
    Compute Mean Average Precision (MAP).

    MAP considers the precision at each relevant item's position.

    Args:
        y_true: Binary relevance labels (1 = relevant, 0 = not)
        y_score: Predicted scores

    Returns:
        MAP score between 0 and 1
    """
    order = np.argsort(y_score)[::-1]
    y_true_sorted = np.take(y_true, order)

    relevant_count = 0
    precision_sum = 0.0
    total_relevant = np.sum(y_true > 0)

    if total_relevant == 0:
        return 0.0

    for i, rel in enumerate(y_true_sorted):
        if rel > 0:
            relevant_count += 1
            precision_at_i = relevant_count / (i + 1)
            precision_sum += precision_at_i

    return float(precision_sum / total_relevant)


def mean_reciprocal_rank(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """
    Compute Mean Reciprocal Rank (MRR).

    MRR measures how early the first relevant item appears.

    Args:
        y_true: Binary relevance labels
        y_score: Predicted scores

    Returns:
        MRR score between 0 and 1
    """
    order = np.argsort(y_score)[::-1]
    y_true_sorted = np.take(y_true, order)

    for i, rel in enumerate(y_true_sorted):
        if rel > 0:
            return 1.0 / (i + 1)

    return 0.0


def precision_at_k(y_true: np.ndarray, y_score: np.ndarray, k: int = 10) -> float:
    """Precision at K: fraction of top-K items that are relevant."""
    order = np.argsort(y_score)[::-1][:k]
    y_true_sorted = np.take(y_true, order)
    return float(np.sum(y_true_sorted > 0) / k)


def recall_at_k(y_true: np.ndarray, y_score: np.ndarray, k: int = 10) -> float:
    """Recall at K: fraction of relevant items found in top-K."""
    total_relevant = np.sum(y_true > 0)
    if total_relevant == 0:
        return 0.0
    order = np.argsort(y_score)[::-1][:k]
    y_true_sorted = np.take(y_true, order)
    return float(np.sum(y_true_sorted > 0) / total_relevant)


def evaluate_ranker(
    y_true_list: list[np.ndarray],
    y_score_list: list[np.ndarray],
    k_values: list[int] | None = None,
) -> RankingMetrics:
    """
    Evaluate a ranking model across multiple queries.

    Args:
        y_true_list: List of relevance arrays (one per query)
        y_score_list: List of score arrays (one per query)
        k_values: Cutoff values for NDCG/Precision (default: [5, 10, 20])

    Returns:
        RankingMetrics with aggregated scores
    """
    if k_values is None:
        k_values = [5, 10, 20]

    n_queries = len(y_true_list)
    metrics = RankingMetrics()

    ndcg_scores = {k: [] for k in k_values}
    map_scores = []
    mrr_scores = []
    prec_scores = {k: [] for k in k_values}
    rec_scores = {k: [] for k in k_values}

    for y_true, y_score in zip(y_true_list, y_score_list):
        for k in k_values:
            ndcg_scores[k].append(ndcg_at_k(y_true, y_score, k))
            prec_scores[k].append(precision_at_k(y_true, y_score, k))
            rec_scores[k].append(recall_at_k(y_true, y_score, k))

        map_scores.append(mean_average_precision(y_true, y_score))
        mrr_scores.append(mean_reciprocal_rank(y_true, y_score))

    # Aggregate
    if 5 in k_values:
        metrics.ndcg_at_5 = float(np.mean(ndcg_scores[5]))
        metrics.precision_at_5 = float(np.mean(prec_scores[5]))
    if 10 in k_values:
        metrics.ndcg_at_10 = float(np.mean(ndcg_scores[10]))
        metrics.precision_at_10 = float(np.mean(prec_scores[10]))
        metrics.recall_at_10 = float(np.mean(rec_scores[10]))
    if 20 in k_values:
        metrics.ndcg_at_20 = float(np.mean(ndcg_scores[20]))

    metrics.map_score = float(np.mean(map_scores))
    metrics.mrr = float(np.mean(mrr_scores))

    logger.info(
        "Ranker evaluation: NDCG@10=%.4f, MAP=%.4f, MRR=%.4f (n=%d queries)",
        metrics.ndcg_at_10, metrics.map_score, metrics.mrr, n_queries,
    )
    return metrics


def evaluate_fairness(
    allocations: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> FairnessReport:
    """
    Evaluate fairness of allocation outcomes.

    Args:
        allocations: List of allocation records with candidate_id
        candidates: List of candidate profiles with demographic info

    Returns:
        FairnessReport with distribution metrics
    """
    report = FairnessReport()

    # Build lookup
    candidate_map = {c.get("id"): c for c in candidates}
    allocated_candidates = [
        candidate_map[a["candidate_id"]]
        for a in allocations
        if a.get("candidate_id") in candidate_map
    ]

    n_allocated = len(allocated_candidates)
    if n_allocated == 0:
        return report

    # Category distribution
    category_counts: dict[str, int] = {}
    for c in allocated_candidates:
        cat = c.get("social_category", "Unknown")
        category_counts[cat] = category_counts.get(cat, 0) + 1
    report.category_distribution = {
        k: v / n_allocated for k, v in category_counts.items()
    }

    # Geographic distribution (by state)
    state_counts: dict[str, int] = {}
    for c in allocated_candidates:
        state = c.get("state", "Unknown")
        state_counts[state] = state_counts.get(state, 0) + 1
    report.geographic_distribution = {
        k: v / n_allocated for k, v in state_counts.items()
    }

    # Rural/Urban ratio
    rural_count = sum(1 for c in allocated_candidates if c.get("is_rural", False))
    report.rural_urban_ratio = {
        "rural": rural_count / n_allocated,
        "urban": (n_allocated - rural_count) / n_allocated,
    }

    # Gini coefficient (on allocation counts per district)
    district_counts = list(state_counts.values())
    if len(district_counts) > 1:
        report.gini_coefficient = _gini(np.array(district_counts, dtype=float))

    # Group parities (category representation vs. candidate pool)
    pool_category: dict[str, int] = {}
    for c in candidates:
        cat = c.get("social_category", "Unknown")
        pool_category[cat] = pool_category.get(cat, 0) + 1
    pool_total = sum(pool_category.values())

    for cat, pool_count in pool_category.items():
        pool_pct = pool_count / pool_total if pool_total > 0 else 0
        alloc_pct = category_counts.get(cat, 0) / n_allocated
        # Parity = alloc_pct / pool_pct (1.0 = perfect parity)
        report.group_parities[cat] = alloc_pct / pool_pct if pool_pct > 0 else 0.0

    logger.info(
        "Fairness evaluation: Gini=%.4f, categories=%d, states=%d",
        report.gini_coefficient, len(category_counts), len(state_counts),
    )
    return report


def _gini(values: np.ndarray) -> float:
    """
    Compute the Gini coefficient.

    0 = perfect equality, 1 = perfect inequality.
    """
    sorted_vals = np.sort(values)
    n = len(sorted_vals)
    if n == 0 or np.sum(sorted_vals) == 0:
        return 0.0
    cumulative = np.cumsum(sorted_vals)
    gini = (2 * np.sum((np.arange(1, n + 1) * sorted_vals)) - (n + 1) * np.sum(sorted_vals))
    gini = gini / (n * np.sum(sorted_vals))
    return float(max(0.0, min(1.0, gini)))
