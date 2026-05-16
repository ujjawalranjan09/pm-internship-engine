"""
Fairness Metrics – Distribution & Equity Analysis
===================================================

Computes metrics to evaluate how equitably allocations are distributed
across social categories, geographies, and demographic groups.

Metrics include:
    - Representation ratio (actual vs expected)
    - Gini coefficient (inequality)
    - Disparate impact ratio
    - Demographic parity difference
    - Allocation rate by group
"""

from __future__ import annotations

import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class GroupMetrics:
    """Metrics for a single demographic group."""

    group_name: str
    total_candidates: int = 0
    allocated_candidates: int = 0
    allocation_rate: float = 0.0
    representation_ratio: float = 0.0  # actual / expected
    average_score: float = 0.0


@dataclass
class FairnessReport:
    """Complete fairness analysis report."""

    # Overall metrics
    gini_coefficient: float = 0.0
    disparate_impact_ratio: float = 0.0
    demographic_parity_difference: float = 0.0

    # Per-group breakdowns
    by_social_category: dict[str, GroupMetrics] = field(default_factory=dict)
    by_district: dict[str, GroupMetrics] = field(default_factory=dict)
    by_state: dict[str, GroupMetrics] = field(default_factory=dict)
    by_rural_urban: dict[str, GroupMetrics] = field(default_factory=dict)
    by_gender: dict[str, GroupMetrics] = field(default_factory=dict)

    # Flags
    violations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for API responses."""
        return {
            "gini_coefficient": round(self.gini_coefficient, 4),
            "disparate_impact_ratio": round(self.disparate_impact_ratio, 4),
            "demographic_parity_difference": round(self.demographic_parity_difference, 4),
            "by_social_category": {
                k: {
                    "total": v.total_candidates,
                    "allocated": v.allocated_candidates,
                    "rate": round(v.allocation_rate, 4),
                    "representation_ratio": round(v.representation_ratio, 4),
                }
                for k, v in self.by_social_category.items()
            },
            "by_rural_urban": {
                k: {
                    "total": v.total_candidates,
                    "allocated": v.allocated_candidates,
                    "rate": round(v.allocation_rate, 4),
                }
                for k, v in self.by_rural_urban.items()
            },
            "violations": self.violations,
        }


class FairnessMetrics:
    """
    Computes fairness and equity metrics for allocations.

    Usage:
        metrics = FairnessMetrics()
        report = metrics.compute(candidates, allocations)
    """

    # Thresholds for violation detection
    MIN_DISPARATE_IMPACT = 0.80  # 4/5ths rule
    MAX_PARITY_DIFFERENCE = 0.10  # 10% max gap
    MIN_REPRESENTATION_RATIO = 0.70

    def compute(
        self,
        candidates: list[dict[str, Any]],
        allocations: list[dict[str, Any]],
        opportunities: list[dict[str, Any]] | None = None,
    ) -> FairnessReport:
        """
        Compute fairness metrics for a set of allocations.

        Args:
            candidates: All candidate dicts (including social_category, district, etc.)
            allocations: Allocation dicts with candidate_id, is_allocated, score.
            opportunities: Opportunity dicts (optional, for context).

        Returns:
            FairnessReport with all metrics and violation flags.
        """
        # Build lookup
        cand_map = {str(c.get("id", i)): c for i, c in enumerate(candidates)}
        allocated_ids = {str(a["candidate_id"]) for a in allocations if a.get("is_allocated", False)}
        alloc_scores = {
            str(a["candidate_id"]): float(a.get("score", 0)) for a in allocations if a.get("is_allocated", False)
        }

        total = len(candidates)
        total_allocated = len(allocated_ids)

        if total == 0:
            return FairnessReport()

        overall_rate = total_allocated / total

        report = FairnessReport()

        # ── By social category ────────────────────────────────────
        report.by_social_category = self._compute_group_metrics(
            candidates,
            allocated_ids,
            alloc_scores,
            key_fn=lambda c: (c.get("social_category") or "general").lower(),
            overall_rate=overall_rate,
        )

        # ── By district ───────────────────────────────────────────
        report.by_district = self._compute_group_metrics(
            candidates,
            allocated_ids,
            alloc_scores,
            key_fn=lambda c: c.get("district") or "unknown",
            overall_rate=overall_rate,
        )

        # ── By state ──────────────────────────────────────────────
        report.by_state = self._compute_group_metrics(
            candidates,
            allocated_ids,
            alloc_scores,
            key_fn=lambda c: c.get("state") or "unknown",
            overall_rate=overall_rate,
        )

        # ── By rural/urban ────────────────────────────────────────
        report.by_rural_urban = self._compute_group_metrics(
            candidates,
            allocated_ids,
            alloc_scores,
            key_fn=lambda c: "rural" if c.get("is_rural", False) else "urban",
            overall_rate=overall_rate,
        )

        # ── By gender ─────────────────────────────────────────────
        report.by_gender = self._compute_group_metrics(
            candidates,
            allocated_ids,
            alloc_scores,
            key_fn=lambda c: (c.get("gender") or "unspecified").lower(),
            overall_rate=overall_rate,
        )

        # ── Overall metrics ───────────────────────────────────────
        report.gini_coefficient = self._gini_coefficient([alloc_scores.get(cid, 0.0) for cid in cand_map])

        # Disparate impact: min group rate / max group rate
        category_rates = [gm.allocation_rate for gm in report.by_social_category.values() if gm.total_candidates > 0]
        if category_rates and max(category_rates) > 0:
            report.disparate_impact_ratio = min(category_rates) / max(category_rates)

        # Demographic parity difference: max gap between groups
        if category_rates:
            report.demographic_parity_difference = max(category_rates) - min(category_rates)

        # ── Violation detection ───────────────────────────────────
        report.violations = self._detect_violations(report)

        return report

    def _compute_group_metrics(
        self,
        candidates: list[dict[str, Any]],
        allocated_ids: set,
        alloc_scores: dict[str, float],
        key_fn,
        overall_rate: float,
    ) -> dict[str, GroupMetrics]:
        """Compute metrics for groups defined by key_fn."""
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for c in candidates:
            groups[key_fn(c)].append(c)

        result = {}
        for group_name, group_candidates in groups.items():
            total = len(group_candidates)
            allocated = sum(1 for c in group_candidates if str(c.get("id", "")) in allocated_ids)
            rate = allocated / total if total > 0 else 0.0

            scores = [
                alloc_scores.get(str(c.get("id", "")), 0.0)
                for c in group_candidates
                if str(c.get("id", "")) in alloc_scores
            ]
            avg_score = float(np.mean(scores)) if scores else 0.0

            representation = rate / overall_rate if overall_rate > 0 else 0.0

            result[group_name] = GroupMetrics(
                group_name=group_name,
                total_candidates=total,
                allocated_candidates=allocated,
                allocation_rate=rate,
                representation_ratio=representation,
                average_score=avg_score,
            )

        return result

    def _gini_coefficient(self, values: list[float]) -> float:
        """
        Compute the Gini coefficient for a list of values.

        0 = perfect equality, 1 = perfect inequality.
        """
        if not values or all(v == 0 for v in values):
            return 0.0

        sorted_vals = sorted(values)
        n = len(sorted_vals)
        cumulative = np.cumsum(sorted_vals)
        total = cumulative[-1]

        if total == 0:
            return 0.0

        gini = (2.0 * sum((i + 1) * v for i, v in enumerate(sorted_vals))) / (n * total) - (n + 1) / n
        return max(0.0, min(1.0, gini))

    def _detect_violations(self, report: FairnessReport) -> list[str]:
        """Detect fairness violations based on thresholds."""
        violations = []

        # Check disparate impact (4/5ths rule) for social categories
        category_rates = {
            k: v.allocation_rate
            for k, v in report.by_social_category.items()
            if v.total_candidates >= 10  # Only check groups with enough data
        }

        if category_rates:
            max_rate = max(category_rates.values())
            for group, rate in category_rates.items():
                if max_rate > 0 and rate / max_rate < self.MIN_DISPARATE_IMPACT:
                    violations.append(
                        f"Disparate impact: {group} allocation rate ({rate:.1%}) "
                        f"is below {self.MIN_DISPARATE_IMPACT:.0%} of the highest group rate ({max_rate:.1%})"
                    )

        # Check representation ratios
        for group_name, gm in report.by_social_category.items():
            if gm.total_candidates >= 10 and gm.representation_ratio < self.MIN_REPRESENTATION_RATIO:
                violations.append(
                    f"Under-representation: {group_name} has representation ratio "
                    f"{gm.representation_ratio:.2f} (threshold: {self.MIN_REPRESENTATION_RATIO})"
                )

        # Check rural/urban parity
        rural = report.by_rural_urban.get("rural")
        urban = report.by_rural_urban.get("urban")
        if rural and urban and rural.total_candidates >= 10 and urban.total_candidates >= 10:
            gap = abs(rural.allocation_rate - urban.allocation_rate)
            if gap > self.MAX_PARITY_DIFFERENCE:
                violations.append(
                    f"Rural-urban parity gap: {gap:.1%} "
                    f"(rural: {rural.allocation_rate:.1%}, urban: {urban.allocation_rate:.1%})"
                )

        # Check Gini
        if report.gini_coefficient > 0.40:
            violations.append(f"High inequality: Gini coefficient is {report.gini_coefficient:.3f} (threshold: 0.40)")

        return violations

    def compute_opportunity_fairness(
        self,
        opportunity: dict[str, Any],
        allocated_candidates: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Compute fairness metrics for a single opportunity's allocations.

        Returns a dict with category distributions and diversity score.
        """
        if not allocated_candidates:
            return {"diversity_score": 0.0, "categories": {}}

        categories = Counter((c.get("social_category") or "general").lower() for c in allocated_candidates)
        total = len(allocated_candidates)

        # Shannon diversity index
        diversity = 0.0
        for count in categories.values():
            p = count / total
            if p > 0:
                diversity -= p * np.log(p)
        # Normalize by max possible diversity
        max_diversity = np.log(max(len(categories), 1))
        diversity_score = diversity / max_diversity if max_diversity > 0 else 0.0

        return {
            "diversity_score": round(float(diversity_score), 4),
            "total_allocated": total,
            "categories": {
                cat: {"count": count, "percentage": round(count / total, 4)} for cat, count in categories.items()
            },
        }
