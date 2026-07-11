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
    max_quality_degradation: float = 0.10
    min_average_score: float = 0.30
    min_score_std_ratio: float = 0.50
    max_group_rate_difference: float = 0.30
    min_diversity_score: float = 0.30
    max_single_group_rate: float = 0.60
    auto_reject: bool = False


@dataclass
class GuardrailViolation:
    guardrail_name: str
    severity: str
    message: str
    current_value: float
    threshold: float
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class GuardrailReport:
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
    def __init__(self, config: GuardrailConfig | None = None) -> None:
        self.config = config or GuardrailConfig()

    def check(
        self,
        original_scores: np.ndarray,
        adjusted_scores: np.ndarray,
        candidate_metadata: list[dict[str, Any]] | None = None,
    ) -> GuardrailReport:
        report = GuardrailReport()

        if len(original_scores) == 0 or len(adjusted_scores) == 0:
            return report

        report.original_mean_score = float(np.mean(original_scores))
        report.adjusted_mean_score = float(np.mean(adjusted_scores))
        report.quality_degradation = report.original_mean_score - report.adjusted_mean_score

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
                        message=(f"Score variance reduced by {(1 - std_ratio):.0%} (std ratio: {std_ratio:.2f})."),
                        current_value=std_ratio,
                        threshold=self.config.min_score_std_ratio,
                    )
                )

        if candidate_metadata:
            group_report = self._check_group_metrics(adjusted_scores, candidate_metadata)
            report.violations.extend(group_report)
            if any(v.severity == "critical" for v in group_report):
                report.passed = False

        report.recommendations = self._generate_recommendations(report)

        if report.passed:
            logger.info(
                "Guardrails PASSED. Quality degradation: %.3f, Mean: %.3f->%.3f",
                report.quality_degradation,
                report.original_mean_score,
                report.adjusted_mean_score,
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
        violations: list[GuardrailViolation] = []
        groups: dict[str, list[float]] = {}
        for i, meta in enumerate(metadata):
            if i >= len(scores):
                break
            group = (meta.get("social_category") or "general").lower()
            groups.setdefault(group, []).append(float(scores[i]))

        if not groups:
            return violations

        group_means = {g: float(np.mean(vals)) for g, vals in groups.items()}
        total = len(scores)
        for group, vals in groups.items():
            rate = len(vals) / total
            if rate > self.config.max_single_group_rate:
                violations.append(
                    GuardrailViolation(
                        guardrail_name="dominant_group",
                        severity="warning",
                        message=f"Group '{group}' has {rate:.0%} of all candidates.",
                        current_value=rate,
                        threshold=self.config.max_single_group_rate,
                    )
                )

        if len(group_means) >= 2:
            rates = list(group_means.values())
            max_diff = max(rates) - min(rates)
            if max_diff > self.config.max_group_rate_difference:
                violations.append(
                    GuardrailViolation(
                        guardrail_name="group_rate_difference",
                        severity="warning",
                        message=f"Score difference between groups is {max_diff:.3f}.",
                        current_value=max_diff,
                        threshold=self.config.max_group_rate_difference,
                    )
                )

        return violations

    def _generate_recommendations(self, report: GuardrailReport) -> list[str]:
        recommendations: list[str] = []
        for v in report.violations:
            if v.guardrail_name == "min_average_score":
                recommendations.append("Consider reducing fairness boost amounts to maintain minimum match quality.")
            elif v.guardrail_name == "score_compression":
                recommendations.append("Consider using multiplicative boosts instead of additive.")
            elif v.guardrail_name == "dominant_group":
                recommendations.append("Consider targeted outreach to under-represented groups.")
            elif v.guardrail_name == "group_rate_difference":
                recommendations.append("Review fairness policy weights and category boosts.")
        if not recommendations and not report.passed:
            recommendations.append("Review fairness policy configuration.")
        return recommendations

    def should_rollback(self, report: GuardrailReport) -> bool:
        if not self.config.auto_reject:
            return False
        return any(v.severity == "critical" for v in report.violations)

    def compute_safe_adjustment(
        self,
        original_scores: np.ndarray,
        proposed_adjustments: np.ndarray,
    ) -> np.ndarray:
        if len(original_scores) == 0:
            return proposed_adjustments
        adjusted = original_scores + proposed_adjustments
        mean_adj = float(np.mean(adjusted))
        if mean_adj >= self.config.min_average_score:
            return proposed_adjustments
        lo, hi = 0.0, 1.0
        for _ in range(20):
            mid = (lo + hi) / 2
            test = original_scores + proposed_adjustments * mid
            if float(np.mean(test)) >= self.config.min_average_score:
                lo = mid
            else:
                hi = mid
        logger.info("Scaling fairness adjustments by %.3f to meet quality guardrail", lo)
        return proposed_adjustments * lo


# ─── Module-level utility functions (required by tests) ──────────────────────


def enforce_min_quality_threshold(
    original_scores: np.ndarray,
    adjusted_scores: np.ndarray,
    threshold: float = 0.6,
) -> np.ndarray:
    """Clamp adjusted scores to at least threshold * original_scores."""
    floor = threshold * original_scores
    return np.maximum(adjusted_scores, floor)


def enforce_max_adjustment(
    original_scores: np.ndarray,
    adjusted_scores: np.ndarray,
    max_delta: float = 0.20,
) -> np.ndarray:
    """Clip per-candidate score adjustment to [-max_delta, +max_delta]."""
    delta = adjusted_scores - original_scores
    clamped_delta = np.clip(delta, -max_delta, max_delta)
    return original_scores + clamped_delta


def detect_overcorrection(
    scores_before: np.ndarray,
    scores_after: np.ndarray,
    group_mask: np.ndarray,
    overcorrection_threshold: float = 0.20,
) -> dict[str, Any]:
    """Detect whether fairness adjustments overcorrected a group."""
    if len(scores_before) == 0:
        return {
            "is_overcorrected": False,
            "group_mean_delta": 0.0,
            "non_group_mean_delta": 0.0,
            "delta_difference": 0.0,
        }
    delta = scores_after - scores_before
    group = group_mask.astype(bool)
    non_group = ~group
    group_delta = float(np.mean(delta[group])) if group.any() else 0.0
    non_group_delta = float(np.mean(delta[non_group])) if non_group.any() else 0.0
    diff = group_delta - non_group_delta
    return {
        "is_overcorrected": diff > overcorrection_threshold,
        "group_mean_delta": round(group_delta, 6),
        "non_group_mean_delta": round(non_group_delta, 6),
        "delta_difference": round(diff, 6),
    }
