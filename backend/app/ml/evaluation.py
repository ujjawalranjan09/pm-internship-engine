"""Offline evaluation utilities for the matching pipeline."""

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


def precision_at_k(relevant: set[int], retrieved: list[int], k: int) -> float:
    top_k = set(retrieved[:k])
    if not top_k:
        return 0.0
    return len(top_k & relevant) / k


def recall_at_k(relevant: set[int], retrieved: list[int], k: int) -> float:
    if not relevant:
        return 0.0
    top_k = set(retrieved[:k])
    return len(top_k & relevant) / len(relevant)


def ndcg_at_k(relevant: set[int], retrieved: list[int], k: int) -> float:
    dcg = 0.0
    for i, item in enumerate(retrieved[:k]):
        if item in relevant:
            dcg += 1.0 / np.log2(i + 2)
    ideal = sum(1.0 / np.log2(i + 2) for i in range(min(len(relevant), k)))
    return dcg / ideal if ideal > 0 else 0.0


def mean_reciprocal_rank(relevant: set[int], retrieved: list[int]) -> float:
    for i, item in enumerate(retrieved):
        if item in relevant:
            return 1.0 / (i + 1)
    return 0.0


def evaluate_batch(
    ground_truth: list[dict[str, Any]],
    predictions: list[dict[str, Any]],
    k: int = 10,
) -> dict[str, float]:
    """Compute aggregate retrieval metrics over a batch."""
    p_scores: list[float] = []
    r_scores: list[float] = []
    n_scores: list[float] = []
    mrr_scores: list[float] = []

    for gt, pred in zip(ground_truth, predictions, strict=False):
        relevant: set[int] = set(gt.get("relevant_ids", []))
        retrieved: list[int] = pred.get("retrieved_ids", [])
        p_scores.append(precision_at_k(relevant, retrieved, k))
        r_scores.append(recall_at_k(relevant, retrieved, k))
        n_scores.append(ndcg_at_k(relevant, retrieved, k))
        mrr_scores.append(mean_reciprocal_rank(relevant, retrieved))

    return {
        f"precision@{k}": float(np.mean(p_scores)),
        f"recall@{k}": float(np.mean(r_scores)),
        f"ndcg@{k}": float(np.mean(n_scores)),
        "mrr": float(np.mean(mrr_scores)),
    }
