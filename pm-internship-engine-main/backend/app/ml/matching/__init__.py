"""
Matching Pipeline Module
========================

End-to-end orchestration of the multi-stage matching process.
Coordinates eligibility filtering, retrieval, ranking, fairness
adjustment, and constrained optimization.
"""

from .matching_pipeline import MatchingPipeline

__all__ = ["MatchingPipeline"]
