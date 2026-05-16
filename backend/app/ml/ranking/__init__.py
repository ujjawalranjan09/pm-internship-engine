"""
Ranking Module
==============

Multi-stage ranking pipeline for candidate-opportunity matching:
    - Heuristic scorer (fast rule-based ranking)
    - ML ranker (LightGBM-based learned ranking)
    - Re-ranker (fairness-aware adjustments)
    - Explainer (human-readable match explanations)
    - Optimizer (constrained allocation via OR-Tools)
"""

from .heuristic_scorer import HeuristicScorer
from .ml_ranker import MLRanker
from .reranker import Reranker
from .explainer import MatchExplainer
from .optimizer import AllocationOptimizer

__all__ = [
    "HeuristicScorer",
    "MLRanker",
    "Reranker",
    "MatchExplainer",
    "AllocationOptimizer",
]
