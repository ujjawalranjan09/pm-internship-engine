"""
PM Internship Scheme - AI/ML Matching Engine
=============================================

A multi-stage matching engine for intelligently allocating candidates
to internship opportunities under the PM Internship Scheme.

Pipeline stages:
    1. Rule-based eligibility filtering
    2. Hybrid retrieval (keyword + semantic)
    3. Feature-based ranking (heuristic + ML)
    4. Fairness-aware re-ranking
    5. Global constrained optimization (OR-Tools)

Usage:
    from app.ml.matching.matching_pipeline import MatchingPipeline
    pipeline = MatchingPipeline(config)
    allocations = pipeline.run(candidates, opportunities)
"""

__version__ = "1.0.0"
