"""
Matching Pipeline – End-to-End 5-Stage Pipeline
=================================================

Orchestrates the full matching process from raw candidate and
opportunity data to final constrained allocations.

Pipeline stages:
    1. Eligibility filtering (rule-based)
    2. Hybrid retrieval (keyword + semantic)
    3. Feature-based ranking (heuristic + ML)
    4. Fairness-aware re-ranking
    5. Global constrained optimization (OR-Tools)

Each stage reduces the candidate-opportunity space and refines
the scores, producing a final allocation that balances quality
and fairness.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from app.ml.feature_engineering.feature_extractor import FeatureExtractor, FeatureVector
from app.ml.ranking.explainer import MatchExplainer, MatchExplanation
from app.ml.ranking.heuristic_scorer import HeuristicScorer
from app.ml.ranking.ml_ranker import MLRanker
from app.ml.ranking.optimizer import AllocationOptimizer, OptimizationResult
from app.ml.ranking.reranker import Reranker, RerankerConfig

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Configuration for the matching pipeline."""

    # Stage 1: Eligibility
    eligibility_fn: Callable | None = None  # custom filter function

    # Stage 2: Retrieval
    retrieval_top_k: int = 100  # candidates per opportunity after retrieval
    use_semantic_retrieval: bool = True
    semantic_weight: float = 0.6  # weight of semantic vs keyword retrieval

    # Stage 3: Ranking
    heuristic_weight: float = 0.4  # weight of heuristic score in blended score
    ml_weight: float = 0.6  # weight of ML score in blended score
    use_ml_ranker: bool = True
    rank_top_k: int = 50  # candidates per opportunity after ranking

    # Stage 4: Re-ranking
    use_reranker: bool = True
    reranker_config: RerankerConfig | None = None

    # Stage 5: Optimization
    optimizer_time_limit: float = 60.0
    use_greedy_fallback: bool = True

    # Explanation
    generate_explanations: bool = True

    # Context (passed to feature extractor)
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineStageResult:
    """Metrics for a single pipeline stage."""

    stage_name: str
    input_count: int
    output_count: int
    duration_seconds: float
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineResult:
    """Full result of a pipeline run."""

    allocations: list[dict[str, Any]] = field(default_factory=list)
    optimization_result: OptimizationResult | None = None
    stage_metrics: list[PipelineStageResult] = field(default_factory=list)
    total_duration_seconds: float = 0.0
    total_candidates: int = 0
    total_opportunities: int = 0
    num_allocated: int = 0
    explanations: dict[str, MatchExplanation] = field(default_factory=dict)


class MatchingPipeline:
    """
    End-to-end matching pipeline.

    Coordinates all stages of the matching process, from raw data
    to final allocations with explanations.

    Usage:
        pipeline = MatchingPipeline(config)
        result = pipeline.run(candidates, opportunities)
    """

    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config = config or PipelineConfig()

        self._feature_extractor = FeatureExtractor()
        self._heuristic_scorer = HeuristicScorer()
        self._ml_ranker: MLRanker | None = None
        self._reranker = Reranker(self.config.reranker_config)
        self._optimizer = AllocationOptimizer(
            time_limit_seconds=self.config.optimizer_time_limit,
            use_greedy_fallback=self.config.use_greedy_fallback,
        )
        self._explainer = MatchExplainer()

        self._stage_metrics: list[PipelineStageResult] = []

    def load_ml_model(self, model_path: str) -> None:
        """Load a trained ML ranker model."""
        self._ml_ranker = MLRanker(model_path=model_path)
        logger.info("ML ranker loaded from %s", model_path)

    def run(
        self,
        candidates: list[dict[str, Any]],
        opportunities: list[dict[str, Any]],
        constraints: dict[str, Any] | None = None,
        blocked_pairs: set[tuple[str, str]] | None = None,
        district_counts: dict[str, int] | None = None,
    ) -> PipelineResult:
        """
        Execute the full matching pipeline.

        Args:
            candidates: List of candidate dicts.
            opportunities: List of opportunity dicts.
            constraints: Allocation constraints (quotas, reserved slots).
            blocked_pairs: Pairs that cannot be allocated.
            district_counts: Current district allocation counts.

        Returns:
            PipelineResult with allocations and metrics.
        """
        total_start = time.time()
        self._stage_metrics = []

        if not candidates or not opportunities:
            return PipelineResult(
                total_candidates=len(candidates),
                total_opportunities=len(opportunities),
            )

        logger.info(
            "Starting matching pipeline: %d candidates × %d opportunities",
            len(candidates),
            len(opportunities),
        )

        # ── Stage 1: Eligibility Filtering ────────────────────────
        candidates, opportunities = self._stage_eligibility(candidates, opportunities)

        if not candidates or not opportunities:
            return PipelineResult(
                total_candidates=len(candidates),
                total_opportunities=len(opportunities),
                stage_metrics=self._stage_metrics,
            )

        # ── Stage 2: Retrieval ────────────────────────────────────
        retrieval_map = self._stage_retrieval(candidates, opportunities)

        # ── Stage 3: Feature Extraction & Ranking ─────────────────
        score_matrix, feature_matrix, candidate_ids, opportunity_ids = self._stage_ranking(
            candidates, opportunities, retrieval_map
        )

        # ── Stage 4: Fairness Re-ranking ──────────────────────────
        if self.config.use_reranker:
            score_matrix = self._stage_reranking(
                score_matrix,
                candidate_ids,
                opportunity_ids,
                candidates,
                district_counts,
            )

        # ── Stage 5: Constrained Optimization ─────────────────────
        opt_result = self._stage_optimization(
            score_matrix,
            candidate_ids,
            opportunity_ids,
            candidates,
            opportunities,
            constraints,
            blocked_pairs,
        )

        # ── Generate Explanations ─────────────────────────────────
        explanations: dict[str, MatchExplanation] = {}
        if self.config.generate_explanations:
            explanations = self._generate_explanations(
                opt_result,
                feature_matrix,
                candidate_ids,
                opportunity_ids,
            )

        # ── Build Final Output ────────────────────────────────────
        allocations = self._build_output(opt_result, explanations)

        total_duration = time.time() - total_start

        result = PipelineResult(
            allocations=allocations,
            optimization_result=opt_result,
            stage_metrics=self._stage_metrics,
            total_duration_seconds=total_duration,
            total_candidates=len(candidates),
            total_opportunities=len(opportunities),
            num_allocated=opt_result.num_allocated,
            explanations=explanations,
        )

        logger.info(
            "Pipeline complete: %d/%d candidates allocated in %.1fs",
            result.num_allocated,
            result.total_candidates,
            total_duration,
        )

        return result

    def _stage_eligibility(
        self,
        candidates: list[dict[str, Any]],
        opportunities: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Stage 1: Filter by eligibility rules."""
        start = time.time()
        input_count = len(candidates) + len(opportunities)

        if self.config.eligibility_fn:
            candidates, opportunities = self.config.eligibility_fn(candidates, opportunities)

        # Basic filters
        candidates = [c for c in candidates if c.get("skills")]
        opportunities = [o for o in opportunities if o.get("is_active", True)]

        output_count = len(candidates) + len(opportunities)
        self._stage_metrics.append(
            PipelineStageResult(
                stage_name="eligibility_filter",
                input_count=input_count,
                output_count=output_count,
                duration_seconds=time.time() - start,
                details={
                    "candidates_remaining": len(candidates),
                    "opportunities_remaining": len(opportunities),
                },
            )
        )

        logger.info("Stage 1 (Eligibility): %d candidates, %d opportunities", len(candidates), len(opportunities))
        return candidates, opportunities

    def _stage_retrieval(
        self,
        candidates: list[dict[str, Any]],
        opportunities: list[dict[str, Any]],
    ) -> dict[str, list[str]]:
        """Stage 2: Build candidate→opportunities retrieval map."""
        start = time.time()

        # For now, build full cross-product (retrieval filtering happens via top_k)
        # In production, use vector search to pre-filter
        retrieval_map: dict[str, list[str]] = {}
        cand_ids = [str(c.get("id", i)) for i, c in enumerate(candidates)]
        opp_ids = [str(o.get("id", i)) for i, o in enumerate(opportunities)]

        for cid in cand_ids:
            retrieval_map[cid] = opp_ids

        self._stage_metrics.append(
            PipelineStageResult(
                stage_name="retrieval",
                input_count=len(candidates) * len(opportunities),
                output_count=sum(len(v) for v in retrieval_map.values()),
                duration_seconds=time.time() - start,
            )
        )

        logger.info("Stage 2 (Retrieval): %d pairs", sum(len(v) for v in retrieval_map.values()))
        return retrieval_map

    def _stage_ranking(
        self,
        candidates: list[dict[str, Any]],
        opportunities: list[dict[str, Any]],
        retrieval_map: dict[str, list[str]],
    ) -> tuple[np.ndarray, np.ndarray, list[str], list[str]]:
        """Stage 3: Extract features and compute scores."""
        start = time.time()

        candidate_ids = [str(c.get("id", i)) for i, c in enumerate(candidates)]
        opportunity_ids = [str(o.get("id", i)) for i, o in enumerate(opportunities)]

        {cid: i for i, cid in enumerate(candidate_ids)}
        opp_id_to_idx = {oid: j for j, oid in enumerate(opportunity_ids)}

        n_cand = len(candidate_ids)
        n_opp = len(opportunity_ids)
        n_features = len(FeatureVector.feature_names())

        score_matrix = np.zeros((n_cand, n_opp), dtype=np.float64)
        feature_matrix = np.zeros((n_cand, n_opp, n_features), dtype=np.float64)

        for i, cand in enumerate(candidates):
            cid = candidate_ids[i]
            for oid in retrieval_map.get(cid, opportunity_ids):
                j = opp_id_to_idx.get(oid)
                if j is None:
                    continue

                opp = opportunities[j]
                fv = self._feature_extractor.extract(cand, opp, self.config.context)
                feature_matrix[i, j] = fv.to_array()

                # Blend heuristic and ML scores
                h_score, _ = self._heuristic_scorer.score(fv)

                if self.config.use_ml_ranker and self._ml_ranker and self._ml_ranker.is_trained:
                    ml_score = (
                        float(self._ml_ranker.predict(fv.to_array().reshape(1, -1), [cid], oid)[0].score)
                        if self._ml_ranker
                        else h_score
                    )
                    blended = self.config.heuristic_weight * h_score + self.config.ml_weight * ml_score
                else:
                    blended = h_score

                score_matrix[i, j] = blended

        # Apply top-k per opportunity
        for j in range(n_opp):
            col = score_matrix[:, j]
            if len(col) > self.config.rank_top_k:
                threshold = np.partition(col, -self.config.rank_top_k)[-self.config.rank_top_k]
                score_matrix[col < threshold, j] = 0.0

        self._stage_metrics.append(
            PipelineStageResult(
                stage_name="ranking",
                input_count=n_cand * n_opp,
                output_count=int(np.count_nonzero(score_matrix)),
                duration_seconds=time.time() - start,
                details={"n_features": n_features},
            )
        )

        logger.info("Stage 3 (Ranking): %d non-zero scores", int(np.count_nonzero(score_matrix)))
        return score_matrix, feature_matrix, candidate_ids, opportunity_ids

    def _stage_reranking(
        self,
        score_matrix: np.ndarray,
        candidate_ids: list[str],
        opportunity_ids: list[str],
        candidates: list[dict[str, Any]],
        district_counts: dict[str, int] | None,
    ) -> np.ndarray:
        """Stage 4: Apply fairness-aware re-ranking."""
        start = time.time()

        cand_meta = {}
        for i, cand in enumerate(candidates):
            cid = candidate_ids[i]
            cand_meta[cid] = {
                "social_category": cand.get("social_category", "general"),
                "is_rural": cand.get("is_rural", False),
                "district": cand.get("district"),
                "gender": cand.get("gender"),
            }

        adjusted_matrix = score_matrix.copy()

        for j, oid in enumerate(opportunity_ids):
            col = score_matrix[:, j]
            nonzero = np.nonzero(col)[0]
            if len(nonzero) == 0:
                continue

            scored_list = [
                {
                    "candidate_id": candidate_ids[i],
                    "opportunity_id": oid,
                    "score": float(col[i]),
                    "rank": 0,
                }
                for i in nonzero
            ]

            reranked = self._reranker.rerank(scored_list, cand_meta, district_counts=district_counts)

            for r in reranked:
                i = candidate_ids.index(r.candidate_id) if r.candidate_id in candidate_ids else -1
                if 0 <= i < len(candidate_ids):
                    adjusted_matrix[i, j] = r.adjusted_score

        self._stage_metrics.append(
            PipelineStageResult(
                stage_name="reranking",
                input_count=int(np.count_nonzero(score_matrix)),
                output_count=int(np.count_nonzero(adjusted_matrix)),
                duration_seconds=time.time() - start,
            )
        )

        logger.info("Stage 4 (Re-ranking): complete")
        return adjusted_matrix

    def _stage_optimization(
        self,
        score_matrix: np.ndarray,
        candidate_ids: list[str],
        opportunity_ids: list[str],
        candidates: list[dict[str, Any]],
        opportunities: list[dict[str, Any]],
        constraints: dict[str, Any] | None,
        blocked_pairs: set[tuple[str, str]] | None,
    ) -> OptimizationResult:
        """Stage 5: Constrained optimization."""
        start = time.time()

        capacities = {}
        for i, opp in enumerate(opportunities):
            oid = opportunity_ids[i]
            capacities[oid] = opp.get("capacity", 1)

        result = self._optimizer.optimize(
            score_matrix=score_matrix,
            candidate_ids=candidate_ids,
            opportunity_ids=opportunity_ids,
            capacities=capacities,
            constraints=constraints,
            blocked_pairs=blocked_pairs,
        )

        self._stage_metrics.append(
            PipelineStageResult(
                stage_name="optimization",
                input_count=len(candidate_ids) * len(opportunity_ids),
                output_count=result.num_allocated,
                duration_seconds=time.time() - start,
                details={
                    "solver_status": result.solver_status,
                    "total_score": result.total_score,
                },
            )
        )

        logger.info(
            "Stage 5 (Optimization): %d allocations, status=%s, total_score=%.2f",
            result.num_allocated,
            result.solver_status,
            result.total_score,
        )
        return result

    def _generate_explanations(
        self,
        opt_result: OptimizationResult,
        feature_matrix: np.ndarray,
        candidate_ids: list[str],
        opportunity_ids: list[str],
    ) -> dict[str, MatchExplanation]:
        """Generate explanations for all allocated pairs."""
        cand_idx = {cid: i for i, cid in enumerate(candidate_ids)}
        opp_idx = {oid: j for j, oid in enumerate(opportunity_ids)}

        explanations = {}
        for alloc in opt_result.allocations:
            if not alloc.is_allocated:
                continue

            i = cand_idx.get(alloc.candidate_id, -1)
            j = opp_idx.get(alloc.opportunity_id, -1)
            if i < 0 or j < 0:
                continue

            fv = FeatureVector.from_array(feature_matrix[i, j])
            explanation = self._explainer.explain(fv, alloc.score)
            key = f"{alloc.candidate_id}:{alloc.opportunity_id}"
            explanations[key] = explanation

        return explanations

    def _build_output(
        self,
        opt_result: OptimizationResult,
        explanations: dict[str, MatchExplanation],
    ) -> list[dict[str, Any]]:
        """Build the final allocation output list."""
        allocations = []

        for alloc in opt_result.allocations:
            key = f"{alloc.candidate_id}:{alloc.opportunity_id}"
            explanation = explanations.get(key)

            allocations.append(
                {
                    "candidate_id": alloc.candidate_id,
                    "opportunity_id": alloc.opportunity_id,
                    "score": alloc.score,
                    "is_allocated": alloc.is_allocated,
                    "explanation": explanation.to_dict() if explanation else None,
                }
            )

        return allocations
