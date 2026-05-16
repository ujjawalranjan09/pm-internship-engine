"""
Fairness guardrails to prevent overcorrection and quality degradation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class GuardrailResult:
    """Result of a guardrail check."""
    passed: bool
    original_mean: float
    adjusted_mean: float
    max_drop: float
    interventions: list[dict[str, Any]]
    message: str


def enforce_min_quality_threshold(
    original_scores: np.ndarray,
    adjusted_scores: np.ndarray,
    threshold: float = 0.6,
) -> tuple[np.ndarray, int]:
    """
    Ensure no score drops below the minimum quality threshold.

    Args:
        original_scores: Original match scores
        adjusted_scores: Fairness-adjusted scores
        threshold: Minimum acceptable score

    Returns:
        Tuple of (corrected_scores, num_interventions)
    """
    corrected = adjusted_scores.copy()
    interventions = 0

    for i in range(len(corrected)):
        if corrected[i] < threshold:
            # Restore to either threshold or 90% of original, whichever is lower
            corrected[i] = max(threshold, original_scores[i] * 0.9)
            interventions += 1

    if interventions > 0:
        logger.warning(
            "Quality guardrail: %d scores restored below threshold %.2f",
            interventions, threshold,
        )

    return corrected, interventions


def enforce_max_adjustment(
    original_scores: np.ndarray,
    adjustments: np.ndarray,
    max_delta: float = 0.15,
) -> np.ndarray:
    """
    Cap individual adjustments to prevent extreme changes.

    Args:
        original_scores: Original match scores
        adjustments: Raw fairness adjustments
        max_delta: Maximum allowed adjustment magnitude

    Returns:
        Capped adjustments array
    """
    capped = np.clip(adjustments, -max_delta, max_delta)
    num_capped = int(np.sum(np.abs(adjustments) > max_delta))
    if num_capped > 0:
        logger.warning(
            "Adjustment cap: %d adjustments capped to ±%.2f",
            num_capped, max_delta,
        )
    return capped


def detect_overcorrection(
    before: np.ndarray,
    after: np.ndarray,
    group_labels: np.ndarray,
    group_name: str = "group",
    max_mean_shift: float = 0.10,
) -> GuardrailResult:
    """
    Detect if fairness re-ranking caused overcorrection.

    Args:
        before: Scores before re-ranking
        after: Scores after re-ranking
        group_labels: Group membership labels
        group_name: Name of the grouping (for logging)
        max_mean_shift: Maximum allowed mean score shift per group

    Returns:
        GuardrailResult with pass/fail and diagnostics
    """
    interventions: list[dict[str, Any]] = []
    overall_passed = True
    max_drop_observed = 0.0

    unique_groups = np.unique(group_labels)

    for group in unique_groups:
        mask = group_labels == group
        before_mean = float(np.mean(before[mask]))
        after_mean = float(np.mean(after[mask]))
        shift = after_mean - before_mean

        if abs(shift) > max_mean_shift:
            overall_passed = False
            max_drop_observed = max(max_drop_observed, abs(shift))
            interventions.append({
                "group": str(group),
                "before_mean": before_mean,
                "after_mean": after_mean,
                "shift": shift,
                "threshold": max_mean_shift,
                "status": "violation",
            })
            logger.warning(
                "Overcorrection detected in %s='%s': shift=%.4f (max=%.4f)",
                group_name, group, shift, max_mean_shift,
            )
        else:
            interventions.append({
                "group": str(group),
                "before_mean": before_mean,
                "after_mean": after_mean,
                "shift": shift,
                "status": "ok",
            })

    return GuardrailResult(
        passed=overall_passed,
        original_mean=float(np.mean(before)),
        adjusted_mean=float(np.mean(after)),
        max_drop=max_drop_observed,
        interventions=interventions,
        message=(
            f"Guardrail {'PASSED' if overall_passed else 'FAILED'}: "
            f"max shift={max_drop_observed:.4f}, threshold={max_mean_shift:.4f}"
        ),
    )


def log_guardrail_intervention(
    candidate_id: Any,
    original_score: float,
    adjusted_score: float,
    corrected_score: float,
    reason: str,
) -> dict[str, Any]:
    """
    Log a guardrail intervention for audit purposes.

    Returns:
        Intervention record dict
    """
    record = {
        "candidate_id": candidate_id,
        "original_score": original_score,
        "adjusted_score": adjusted_score,
        "corrected_score": corrected_score,
        "delta_from_original": corrected_score - original_score,
        "delta_from_adjusted": corrected_score - adjusted_score,
        "reason": reason,
        "intervened": corrected_score != adjusted_score,
    }
    if record["intervened"]:
        logger.info(
            "Guardrail intervention for candidate %s: %.3f → %.3f → %.3f (%s)",
            candidate_id, original_score, adjusted_score, corrected_score, reason,
        )
    return record


def apply_all_guardrails(
    original_scores: np.ndarray,
    adjusted_scores: np.ndarray,
    min_threshold: float = 0.6,
    max_delta: float = 0.15,
) -> tuple[np.ndarray, dict[str, Any]]:
    """
    Apply all guardrails in sequence.

    Args:
        original_scores: Original match scores
        adjusted_scores: Fairness-adjusted scores
        min_threshold: Minimum quality threshold
        max_delta: Maximum allowed adjustment

    Returns:
        Tuple of (final_scores, guardrail_report)
    """
    # Step 1: Cap adjustments
    raw_adjustments = adjusted_scores - original_scores
    capped_adjustments = enforce_max_adjustment(original_scores, raw_adjustments, max_delta)
    capped_scores = original_scores + capped_adjustments

    # Step 2: Enforce minimum quality
    final_scores, num_quality_interventions = enforce_min_quality_threshold(
        original_scores, capped_scores, min_threshold,
    )

    # Step 3: Compute statistics
    total_interventions = int(np.sum(final_scores != adjusted_scores))
    max_shift = float(np.max(np.abs(final_scores - original_scores)))

    report = {
        "total_candidates": len(original_scores),
        "total_interventions": total_interventions,
        "quality_interventions": num_quality_interventions,
        "max_shift": max_shift,
        "mean_original": float(np.mean(original_scores)),
        "mean_final": float(np.mean(final_scores)),
        "mean_adjustment": float(np.mean(final_scores - original_scores)),
    }

    if total_interventions > 0:
        logger.info("Guardrails: %d total interventions applied", total_interventions)

    return final_scores, report
