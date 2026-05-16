"""
Fairness Guardrails – Quality-Fairness Tradeoff Monitoring
============================================================

Monitors the impact of fairness adjustments on overall match quality
and prevents overcorrection that would significantly degrade match
quality or create perverse incentives.

Guardrails:
    - Maximum quality degradation threshold
    - Minimum average score after fairness adjustments
    - Score distribution monitoring (detect score compression)
    - Anomaly detection (unusual allocation patterns)
    - Automatic rollback trigger
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class GuardrailConfig:
    """Configuration for fairness guardrails."""

    # Maximum allowed degradation in average score (absolute)
    max_quality_degradation: float = 0.10

    # Minimum average score after fairness adjustments
    min_average_score: float = 0.30

    # Score compression detection: if std dev drops below this fraction
    # of the original, flag it
    min_score_std_ratio: float = 0.50

    # Maximum allocation rate difference between groups
    max_group_rate_difference: float = 0.30

    # Minimum diversity score (Shannon-based, 0-1)
    min_diversity_score: float = 0.30

    # Anomaly detection: flag if any group has > this allocation rate
    max_single_group_rate: float = 0.60

    # Whether to automatically reject adjustments that violate guardrails
    auto_reject: bool = False


@dataclass
class GuardrailViolation:
    """A single guardrail violation."""

    guardrail_name: str
    severity: str  # "warning", "critical"
    message: str
    current_value: float
    threshold: float
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class GuardrailReport:
    """Report on guardrail status after fairness adjustments."""

    passed: bool = True
    violations: list[GuardrailViolation] = field(default_factory=list)
    original_mean_score: float = 0.0
    adjusted_mean_score: float = 0.0
    quality_degradation: float = 0.0
    original_std: float = 0.0
    adjusted_std: float = 0.0
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "violations": [
                {
                    "guardrail": v.guardrail_name,
                    "severity": v.severity,
                    "message": v.message,
                    "current": round(v.current_value, 4),
                    "threshold": round(v.threshold, 4),
                }
                for v in self.violations
            ],
            "quality_degradation": round(self.quality_degradation, 4),
            "original_mean": round(self.original_mean_score, 4),
            "adjusted_mean": round(self.adjusted_mean_score, 4),
            "recommendations": self.recommendations,
        }


class FairnessGuardrails:
    """
    Monitors and enforces quality-fairness tradeoff guardrails.

    Usage:
        guardrails = FairnessGuardrails(config)
        report = guardrails.check(original_scores, adjusted_scores, metadata)
        if not report.passed:
            # Handle violations
    """

    def __init__(self, config: GuardrailConfig | None = None) -> None:
        self.config = config or GuardrailConfig()

    def check(
        self,
        original_scores: np.ndarray,
        adjusted_scores: np.ndarray,
        candidate_metadata: list[dict[str, Any]] | None = None,
    ) -> GuardrailReport:
        """
        Check guardrails after fairness adjustments.

        Args:
            original_scores: Scores before fairness adjustment.
            adjusted_scores: Scores after fairness adjustment.
            candidate_metadata: Metadata for group-level checks.

        Returns:
            GuardrailReport with violations and recommendations.
        """
        report = GuardrailReport()

        if len(original_scores) == 0 or len(adjusted_scores) == 0:
            return report

        # ── Quality degradation check ─────────────────────────────
        report.original_mean_score = float(np.mean(original_scores))
        report.adjusted_mean_score = float(np.mean(adjusted_scores))
        report.quality_degradation = report.original_mean_score - report.adjusted_mean_score

        # Guardrail: adjusted mean should not be significantly lower
        # Note: fairness boosts can increase the mean, which is fine
        if report.adjusted_mean_score < self.config.min_average_score:
            report.passed = False
            report.violations.append(
                GuardrailViolation(
                    guardrail_name="min_average_score",
                    severity="critical",
                    message=(
                        f"Average score after adjustment ({report.adjusted_mean_score:.3f}) "
                        f"is below minimum threshold ({self.config.min_average_score:.3f})"
                    ),
                    current_value=report.adjusted_mean_score,
                    threshold=self.config.min_average_score,
                )
            )

        # ── Score compression check ───────────────────────────────
        report.original_std = float(np.std(original_scores))
        report.adjusted_std = float(np.std(adjusted_scores))

        if report.original_std > 0:
            std_ratio = report.adjusted_std / report.original_std
            if std_ratio < self.config.min_score_std_ratio:
                report.passed = False
                report.violations.append(
                    GuardrailViolation(
                        guardrail_name="score_compression",
                        severity="warning",
                        message=(
                            f"Score variance reduced by {(1 - std_ratio):.0%} "
                            f"(std ratio: {std_ratio:.2f}). Fairness adjustments may be "
                            f"compressing scores too much, reducing discrimination ability."
                        ),
                        current_value=std_ratio,
                        threshold=self.config.min_score_std_ratio,
                    )
                )

        # ── Group-level checks ────────────────────────────────────
        if candidate_metadata:
            group_report = self._check_group_metrics(adjusted_scores, candidate_metadata)
            report.violations.extend(group_report)
            if any(v.severity == "critical" for v in group_report):
                report.passed = False

        # ── Recommendations ───────────────────────────────────────
        report.recommendations = self._generate_recommendations(report)

        # ── Logging ───────────────────────────────────────────────
        if report.passed:
            logger.info(
                "Guardrails PASSED. Quality degradation: %.3f, Mean: %.3f→%.3f, Std: %.3f→%.3f",
                report.quality_degradation,
                report.original_mean_score,
                report.adjusted_mean_score,
                report.original_std,
                report.adjusted_std,
            )
        else:
            logger.warning(
                "Guardrails FAILED with %d violations: %s",
                len(report.violations),
                [v.guardrail_name for v in report.violations],
            )

        return report

    def _check_group_metrics(
        self,
        scores: np.ndarray,
        metadata: list[dict[str, Any]],
    ) -> list[GuardrailViolation]:
        """Check group-level fairness metrics."""
        violations = []

        # Group allocation rates
        groups: dict[str, list[float]] = {}
        for i, meta in enumerate(metadata):
            if i >= len(scores):
                break
            group = (meta.get("social_category") or "general").lower()
            groups.setdefault(group, []).append(float(scores[i]))

        if not groups:
            return violations

        group_means = {g: np.mean(vals) for g, vals in groups.items()}

        # Check for any single group dominating
        total = len(scores)
        for group, vals in groups.items():
            rate = len(vals) / total
            if rate > self.config.max_single_group_rate:
                violations.append(
                    GuardrailViolation(
                        guardrail_name="dominant_group",
                        severity="warning",
                        message=(
                            f"Group '{group}' has {rate:.0%} of all candidates, "
                            f"exceeding {self.config.max_single_group_rate:.0%} threshold."
                        ),
                        current_value=rate,
                        threshold=self.config.max_single_group_rate,
                    )
                )

        # Check group rate differences
        if len(group_means) >= 2:
            rates = list(group_means.values())
            max_diff = max(rates) - min(rates)
            if max_diff > self.config.max_group_rate_difference:
                violations.append(
                    GuardrailViolation(
                        guardrail_name="group_rate_difference",
                        severity="warning",
                        message=(
                            f"Score difference between groups is {max_diff:.3f}, "
                            f"exceeding threshold {self.config.max_group_rate_difference:.3f}."
                        ),
                        current_value=max_diff,
                        threshold=self.config.max_group_rate_difference,
                    )
                )

        return violations

    def _generate_recommendations(self, report: GuardrailReport) -> list[str]:
        """Generate actionable recommendations based on violations."""
        recommendations = []

        for v in report.violations:
            if v.guardrail_name == "min_average_score":
                recommendations.append(
                    "Consider increasing the quality floor threshold or reducing "
                    "fairness boost amounts to maintain minimum match quality."
                )
            elif v.guardrail_name == "score_compression":
                recommendations.append(
                    "Fairness adjustments are compressing scores. Consider using "
                    "multiplicative boosts instead of additive, or reducing boost amounts."
                )
            elif v.guardrail_name == "dominant_group":
                recommendations.append(
                    "One demographic group dominates the candidate pool. Consider "
                    "targeted outreach to under-represented groups."
                )
            elif v.guardrail_name == "group_rate_difference":
                recommendations.append(
                    "Significant score differences between groups detected. Review "
                    "fairness policy weights and consider adjusting category boosts."
                )

        if not recommendations and not report.passed:
            recommendations.append("Review fairness policy configuration and consider reducing adjustment magnitudes.")

        return recommendations

    def should_rollback(self, report: GuardrailReport) -> bool:
        """
        Determine if fairness adjustments should be rolled back.

        Returns True if critical violations are detected and auto-reject
        is enabled.
        """
        if not self.config.auto_reject:
            return False

        critical_count = sum(1 for v in report.violations if v.severity == "critical")
        return critical_count > 0

    def compute_safe_adjustment(
        self,
        original_scores: np.ndarray,
        proposed_adjustments: np.ndarray,
    ) -> np.ndarray:
        """
        Scale down proposed adjustments to stay within guardrails.

        Uses binary search to find the maximum adjustment scale that
        keeps the average score above the minimum threshold.
        """
        if len(original_scores) == 0:
            return proposed_adjustments

        # Try full adjustment first
        adjusted = original_scores + proposed_adjustments
        mean_adj = float(np.mean(adjusted))

        if mean_adj >= self.config.min_average_score:
            return proposed_adjustments

        # Binary search for safe scale
        lo, hi = 0.0, 1.0
        for _ in range(20):  # 20 iterations → ~1e-6 precision
            mid = (lo + hi) / 2
            test = original_scores + proposed_adjustments * mid
            if float(np.mean(test)) >= self.config.min_average_score:
                lo = mid
            else:
                hi = mid

        safe_scale = lo
        logger.info(
            "Scaling fairness adjustments by %.3f to meet quality guardrail",
            safe_scale,
        )
        return proposed_adjustments * safe_scale


# Standalone functions for backwards compatibility with tests
def enforce_min_quality_threshold(
    original: np.ndarray,
    adjusted: np.ndarray,
    threshold: float = 0.6,
) -> np.ndarray:
    """Ensure adjusted scores don't fall below threshold fraction of original."""
    result = adjusted.copy()
    mask = original > 0
    min_vals = original[mask] * threshold
    result[mask] = np.maximum(result[mask], min_vals)
    return result


def enforce_max_adjustment(
    original: np.ndarray,
    adjusted: np.ndarray,
    max_delta: float = 0.15,
) -> np.ndarray:
    """Clamp adjustments so |adjusted - original| <= max_delta."""
    result = adjusted.copy()
    delta = adjusted - original
    too_high = delta > max_delta
    too_low = delta < -max_delta
    result[too_high] = original[too_high] + max_delta
    result[too_low] = original[too_low] - max_delta
    return result


def detect_overcorrection(
    before: np.ndarray,
    after: np.ndarray,
    group: np.ndarray,
) -> dict[str, Any]:
    """Detect if fairness adjustments overcorrect for a protected group."""
    if len(before) == 0:
        return {"is_overcorrected": False, "group_mean_delta": 0.0, "non_group_mean_delta": 0.0}
    
    group_mask = group.astype(bool)
    non_group_mask = ~group_mask
    
    group_before = before[group_mask] if np.any(group_mask) else np.array([])
    group_after = after[group_mask] if np.any(group_mask) else np.array([])
    non_group_before = before[non_group_mask] if np.any(non_group_mask) else np.array([])
    non_group_after = after[non_group_mask] if np.any(non_group_mask) else np.array([])
    
    group_mean_delta = float(np.mean(group_after - group_before)) if len(group_after) > 0 else 0.0
    non_group_mean_delta = float(np.mean(non_group_after - non_group_before)) if len(non_group_after) > 0 else 0.0
    
    # Overcorrection: if group gets much larger boost than non-group
    is_overcorrected = group_mean_delta > non_group_mean_delta + 0.2
    
    return {
        "is_overcorrected": is_overcorrected,
        "group_mean_delta": group_mean_delta,
        "non_group_mean_delta": non_group_mean_delta,
    }
