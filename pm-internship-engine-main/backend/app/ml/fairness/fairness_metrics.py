"""
Fairness Metrics – Allocation Equity Analysis
==============================================

Computes fairness and equity metrics for the PM Internship Scheme
allocation process, covering:

    - Category-wise allocation rates (SC/ST/OBC/General)
    - Geographic distribution (district/state level)
    - Gender distribution
    - Rural/urban ratio
    - Gini coefficient for allocation inequality
    - Concentration index

These metrics feed into the admin dashboard and periodic fairness
reports.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class FairnessMetricsReport:
    overall_fairness_score: float = 0.0
    gini_coefficient: float = 0.0
    category_distribution: dict[str, Any] = field(default_factory=dict)
    geographic_distribution: dict[str, Any] = field(default_factory=dict)
    gender_distribution: dict[str, Any] = field(default_factory=dict)
    rural_urban_ratio_data: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_fairness_score": round(self.overall_fairness_score, 4),
            "gini_coefficient": round(self.gini_coefficient, 4),
            "category_distribution": self.category_distribution,
            "geographic_distribution": self.geographic_distribution,
            "gender_distribution": self.gender_distribution,
            "rural_urban_ratio": self.rural_urban_ratio_data,
            "recommendations": self.recommendations,
        }


# ─── Core metric functions ────────────────────────────────────────────────────


def gini_coefficient(values: np.ndarray) -> float:
    """Compute Gini coefficient for an allocation distribution."""
    arr = np.clip(np.asarray(values, dtype=float), 0, None)
    if len(arr) == 0 or arr.sum() == 0:
        return 0.0
    sorted_arr = np.sort(arr)
    n = len(sorted_arr)
    total = sorted_arr.sum()
    gini = (2.0 * float(np.sum(np.arange(1, n + 1) * sorted_arr))) / (n * total) - (n + 1) / n
    return float(max(0.0, min(1.0, gini)))


def concentration_index(opportunity_counts: dict[str, int]) -> float:
    """Normalised Herfindahl-Hirschman Index (0=dispersed, 1=concentrated)."""
    if not opportunity_counts:
        return 0.0
    total = sum(opportunity_counts.values())
    if total == 0:
        return 0.0
    shares = [v / total for v in opportunity_counts.values()]
    n = len(shares)
    raw_hhi = sum(s**2 for s in shares)
    if n == 1:
        return 1.0
    normalized = (raw_hhi - 1.0 / n) / (1.0 - 1.0 / n)
    return float(max(0.0, min(1.0, normalized)))


def category_distribution(
    allocations: pd.DataFrame,
    candidates: pd.DataFrame,
    category_col: str = "category",
) -> dict[str, Any]:
    """Allocation rates broken down by social category."""
    if category_col not in candidates.columns:
        return {}
    allocated_ids = set(allocations["candidate_id"].astype(str))
    result: dict[str, Any] = {}
    for cat, group in candidates.groupby(category_col):
        total = len(group)
        alloc = sum(1 for cid in group["candidate_id"].astype(str) if cid in allocated_ids)
        result[str(cat)] = {
            "total": total,
            "allocated": alloc,
            "rate": round(alloc / total, 4) if total else 0.0,
        }
    return result


def geographic_distribution(
    allocations: pd.DataFrame,
    candidates: pd.DataFrame,
    geo_col: str = "district",
) -> dict[str, Any]:
    """Allocation rates broken down by geography."""
    if geo_col not in candidates.columns:
        return {}
    allocated_ids = set(allocations["candidate_id"].astype(str))
    result: dict[str, Any] = {}
    for district, group in candidates.groupby(geo_col):
        total = len(group)
        alloc = sum(1 for cid in group["candidate_id"].astype(str) if cid in allocated_ids)
        result[str(district)] = {
            "total": total,
            "allocated": alloc,
            "rate": round(alloc / total, 4) if total else 0.0,
        }
    return result


def gender_distribution(
    allocations: pd.DataFrame,
    candidates: pd.DataFrame,
    gender_col: str = "gender",
) -> dict[str, Any]:
    """Allocation rates broken down by gender."""
    if gender_col not in candidates.columns:
        return {}
    allocated_ids = set(allocations["candidate_id"].astype(str))
    result: dict[str, Any] = {}
    for gender, group in candidates.groupby(gender_col):
        total = len(group)
        alloc = sum(1 for cid in group["candidate_id"].astype(str) if cid in allocated_ids)
        result[str(gender)] = {
            "total": total,
            "allocated": alloc,
            "rate": round(alloc / total, 4) if total else 0.0,
        }
    return result


def rural_urban_ratio(
    allocations: pd.DataFrame,
    rural_col: str = "is_rural",
) -> dict[str, Any]:
    """Rural vs urban split of allocated candidates."""
    if rural_col not in allocations.columns:
        return {"error": f"column '{rural_col}' not found"}
    rural_count = int(allocations[rural_col].sum())
    total = len(allocations)
    urban_count = total - rural_count
    rural_fraction = rural_count / total if total else 0.0
    return {
        "rural_count": rural_count,
        "urban_count": urban_count,
        "total": total,
        "rural_fraction": round(rural_fraction, 4),
        "urban_fraction": round(1.0 - rural_fraction, 4),
    }


def compute_all_fairness_metrics(
    allocations: pd.DataFrame,
    candidates: pd.DataFrame | None = None,
) -> FairnessMetricsReport:
    """Compute all fairness metrics and return a structured report."""
    report = FairnessMetricsReport()
    if candidates is None or len(candidates) == 0:
        return report
    allocated_ids = set(allocations["candidate_id"].astype(str))
    alloc_flags = np.array([1.0 if str(cid) in allocated_ids else 0.0 for cid in candidates["candidate_id"]])
    report.gini_coefficient = gini_coefficient(alloc_flags)
    report.category_distribution = category_distribution(allocations, candidates)
    report.geographic_distribution = geographic_distribution(allocations, candidates)
    report.gender_distribution = gender_distribution(allocations, candidates)
    if "is_rural" in allocations.columns:
        report.rural_urban_ratio_data = rural_urban_ratio(allocations)
    elif "is_rural" in candidates.columns:
        merged = allocations.merge(candidates[["candidate_id", "is_rural"]], on="candidate_id", how="left")
        report.rural_urban_ratio_data = rural_urban_ratio(merged)
    report.overall_fairness_score = round(1.0 - report.gini_coefficient, 4)
    if report.gini_coefficient > 0.5:
        report.recommendations.append(
            "High inequality detected — consider targeted boosts for under-represented groups."
        )
    if report.category_distribution:
        rates = [v["rate"] for v in report.category_distribution.values() if v["total"] > 0]
        if rates and max(rates) > 0 and min(rates) / max(rates) < 0.8:
            report.recommendations.append(
                "Category allocation rates differ significantly — review category boost policies."
            )
    return report


class FairnessMetricsCalculator:
    """Stateful calculator for computing fairness metrics over an allocation cycle."""

    def __init__(self, cycle_id: int | None = None) -> None:
        self.cycle_id = cycle_id

    def compute(
        self,
        allocations: pd.DataFrame,
        candidates: pd.DataFrame,
    ) -> FairnessMetricsReport:
        return compute_all_fairness_metrics(allocations, candidates)

    def aggregate_by(
        self,
        df: pd.DataFrame,
        group_col: str,
        value_col: str,
        agg_fn: Callable[[pd.Series], Any],
    ) -> dict[str, Any]:
        if group_col not in df.columns or value_col not in df.columns:
            return {}
        return {str(k): agg_fn(g[value_col]) for k, g in df.groupby(group_col)}
