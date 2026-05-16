"""
Fairness metrics for evaluating allocation equity.

Computes distributional fairness metrics across categories, geographies,
and other demographic dimensions.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class FairnessReport:
    """Comprehensive fairness report for an allocation."""
    category_distribution: Dict[str, Dict[str, float]]
    geographic_distribution: Dict[str, Dict[str, float]]
    rural_urban_ratio: Dict[str, float]
    gini_coefficient: float
    concentration_index: float
    gender_distribution: Dict[str, Dict[str, float]]
    overall_fairness_score: float
    recommendations: List[str]
    raw_metrics: Dict[str, Any] = field(default_factory=dict)


def category_distribution(
    allocations: pd.DataFrame,
    candidates: pd.DataFrame,
) -> Dict[str, Dict[str, float]]:
    """
    Compute distribution of allocations across social categories.

    Args:
        allocations: DataFrame with candidate_id, opportunity_id columns.
        candidates: DataFrame with candidate_id, category columns.

    Returns:
        Dict mapping category to {allocated, total, allocation_rate, expected_rate}.
    """
    if "category" not in candidates.columns:
        return {}

    cand_with_cat = candidates[["candidate_id", "category"]].copy()
    allocated_ids = set(allocations["candidate_id"].unique())
    cand_with_cat["is_allocated"] = cand_with_cat["candidate_id"].isin(allocated_ids)

    total = len(candidates)
    result = {}

    for category, group in cand_with_cat.groupby("category"):
        cat_total = len(group)
        cat_allocated = int(group["is_allocated"].sum())
        expected_rate = cat_total / total if total > 0 else 0.0

        result[str(category)] = {
            "total_candidates": cat_total,
            "allocated": cat_allocated,
            "allocation_rate": cat_allocated / cat_total if cat_total > 0 else 0.0,
            "expected_rate": expected_rate,
            "representation_gap": (cat_allocated / len(allocated_ids) if len(allocated_ids) > 0 else 0.0) - expected_rate,
        }

    return result


def geographic_distribution(
    allocations: pd.DataFrame,
    candidates: pd.DataFrame,
) -> Dict[str, Dict[str, float]]:
    """
    Compute distribution of allocations across geographic regions.

    Args:
        allocations: DataFrame with candidate_id column.
        candidates: DataFrame with candidate_id, district columns.

    Returns:
        Dict mapping district to {allocated, total, allocation_rate, share}.
    """
    geo_col = None
    for col in ["district", "state", "region"]:
        if col in candidates.columns:
            geo_col = col
            break

    if geo_col is None:
        return {}

    cand_geo = candidates[["candidate_id", geo_col]].copy()
    allocated_ids = set(allocations["candidate_id"].unique())
    cand_geo["is_allocated"] = cand_geo["candidate_id"].isin(allocated_ids)

    total_allocated = len(allocated_ids)
    result = {}

    for region, group in cand_geo.groupby(geo_col):
        region_total = len(group)
        region_allocated = int(group["is_allocated"].sum())

        result[str(region)] = {
            "total_candidates": region_total,
            "allocated": region_allocated,
            "allocation_rate": region_allocated / region_total if region_total > 0 else 0.0,
            "share_of_allocations": region_allocated / total_allocated if total_allocated > 0 else 0.0,
            "share_of_candidates": region_total / len(candidates) if len(candidates) > 0 else 0.0,
        }

    return result


def rural_urban_ratio(allocations: pd.DataFrame) -> Dict[str, float]:
    """
    Compute rural vs urban allocation ratios.

    Args:
        allocations: DataFrame with candidate_id and is_rural column.

    Returns:
        Dict with rural/urban counts and ratios.
    """
    if "is_rural" not in allocations.columns:
        return {"error": "is_rural column not found"}

    rural_mask = allocations["is_rural"].astype(bool)
    rural_count = int(rural_mask.sum())
    urban_count = int((~rural_mask).sum())
    total = rural_count + urban_count

    return {
        "rural_count": rural_count,
        "urban_count": urban_count,
        "total": total,
        "rural_fraction": rural_count / total if total > 0 else 0.0,
        "urban_fraction": urban_count / total if total > 0 else 0.0,
        "rural_urban_ratio": rural_count / urban_count if urban_count > 0 else float("inf"),
    }


def gini_coefficient(values: np.ndarray) -> float:
    """
    Compute the Gini coefficient for a distribution.

    A value of 0 means perfect equality; 1 means maximum inequality.

    Args:
        values: Array of non-negative values (e.g., allocation counts per group).

    Returns:
        Gini coefficient in [0, 1].
    """
    values = np.asarray(values, dtype=float)
    if len(values) == 0:
        return 0.0

    values = values[values >= 0]
    if len(values) == 0 or np.sum(values) == 0:
        return 0.0

    values = np.sort(values)
    n = len(values)
    cumulative = np.cumsum(values)
    total = cumulative[-1]

    if total == 0:
        return 0.0

    gini = 1.0 - 2.0 * np.sum(cumulative) / (n * total) + 1.0 / n
    return float(np.clip(gini, 0.0, 1.0))


def concentration_index(opportunities_by_region: Dict[str, int]) -> float:
    """
    Compute the Herfindahl-Hirschman Index (HHI) concentration index.

    Measures how concentrated opportunities are across regions.
    Lower values indicate more distributed allocation.

    Args:
        opportunities_by_region: Dict mapping region to number of opportunities.

    Returns:
        HHI concentration index in [0, 1]. 1 = all in one region.
    """
    values = list(opportunities_by_region.values())
    total = sum(values)

    if total == 0:
        return 0.0

    shares = [v / total for v in values]
    hhi = sum(s ** 2 for s in shares)

    # Normalize: HHI ranges from 1/n to 1
    n = len(values)
    if n <= 1:
        return 1.0

    min_hhi = 1.0 / n
    normalized = (hhi - min_hhi) / (1.0 - min_hhi)
    return float(np.clip(normalized, 0.0, 1.0))


def gender_distribution(
    allocations: pd.DataFrame,
    candidates: pd.DataFrame,
) -> Dict[str, Dict[str, float]]:
    """
    Compute gender distribution of allocations.

    Args:
        allocations: DataFrame with candidate_id column.
        candidates: DataFrame with candidate_id, gender columns.

    Returns:
        Dict mapping gender to allocation statistics.
    """
    if "gender" not in candidates.columns:
        return {}

    cand_gender = candidates[["candidate_id", "gender"]].copy()
    allocated_ids = set(allocations["candidate_id"].unique())
    cand_gender["is_allocated"] = cand_gender["candidate_id"].isin(allocated_ids)

    total_allocated = len(allocated_ids)
    result = {}

    for gender, group in cand_gender.groupby("gender"):
        g_total = len(group)
        g_allocated = int(group["is_allocated"].sum())

        result[str(gender)] = {
            "total_candidates": g_total,
            "allocated": g_allocated,
            "allocation_rate": g_allocated / g_total if g_total > 0 else 0.0,
            "share_of_allocations": g_allocated / total_allocated if total_allocated > 0 else 0.0,
            "share_of_candidates": g_total / len(candidates) if len(candidates) > 0 else 0.0,
        }

    return result


def compute_all_fairness_metrics(
    allocations: pd.DataFrame,
    candidates: Optional[pd.DataFrame] = None,
) -> FairnessReport:
    """
    Compute all fairness metrics and generate a comprehensive report.

    Args:
        allocations: DataFrame with allocation results (candidate_id, opportunity_id, score).
        candidates: DataFrame with candidate profiles. If None, only allocation-level metrics
                    are computed.

    Returns:
        FairnessReport with all computed metrics and recommendations.
    """
    recommendations = []

    cat_dist = {}
    geo_dist = {}
    gender_dist = {}

    if candidates is not None:
        cat_dist = category_distribution(allocations, candidates)
        geo_dist = geographic_distribution(allocations, candidates)
        gender_dist = gender_distribution(allocations, candidates)

    rural_urban = rural_urban_ratio(allocations)

    # Gini on allocation counts per district
    gini = 0.0
    if geo_dist:
        district_counts = np.array([
            d["allocated"] for d in geo_dist.values()
        ], dtype=float)
        gini = gini_coefficient(district_counts)

        if gini > 0.4:
            recommendations.append(
                f"Geographic inequality is high (Gini={gini:.2f}). "
                "Consider increasing district-level diversity targets."
            )

    # Concentration index on opportunities
    conc = 0.0
    if geo_dist:
        opp_by_region = {k: v["allocated"] for k, v in geo_dist.items()}
        conc = concentration_index(opp_by_region)

        if conc > 0.3:
            recommendations.append(
                f"Opportunity concentration is high (HHI={conc:.2f}). "
                "Consider distributing opportunities more evenly."
            )

    # Category balance check
    if cat_dist:
        allocation_rates = [v["allocation_rate"] for v in cat_dist.values()]
        if allocation_rates:
            rate_gini = gini_coefficient(np.array(allocation_rates))
            if rate_gini > 0.15:
                recommendations.append(
                    f"Category allocation rates are imbalanced (Gini={rate_gini:.2f}). "
                    "Consider category-based balancing in re-ranking."
                )

    # Gender balance check
    if gender_dist:
        female_data = gender_dist.get("female", gender_dist.get("Female", {}))
        if female_data:
            female_share = female_data.get("share_of_allocations", 0.0)
            if female_share < 0.33:
                recommendations.append(
                    f"Female representation is {female_share:.1%} (target: 33%). "
                    "Consider female participation uplift."
                )

    # Rural check
    if "rural_fraction" in rural_urban:
        rural_frac = rural_urban["rural_fraction"]
        if rural_frac < 0.25:
            recommendations.append(
                f"Rural candidate fraction is {rural_frac:.1%} (target: 25%). "
                "Consider rural preference in policy."
            )

    if not recommendations:
        recommendations.append("All fairness metrics are within acceptable ranges.")

    # Overall fairness score (0-1, higher = more fair)
    component_scores = []
    component_scores.append(1.0 - min(gini, 1.0))
    component_scores.append(1.0 - min(conc, 1.0))
    if cat_dist:
        cat_gini = gini_coefficient(np.array([v["allocation_rate"] for v in cat_dist.values()]))
        component_scores.append(1.0 - min(cat_gini, 1.0))
    if gender_dist:
        female_data = gender_dist.get("female", gender_dist.get("Female", {}))
        female_share = female_data.get("share_of_allocations", 0.0)
        component_scores.append(min(female_share / 0.33, 1.0))

    overall_score = float(np.mean(component_scores)) if component_scores else 0.5

    return FairnessReport(
        category_distribution=cat_dist,
        geographic_distribution=geo_dist,
        rural_urban_ratio=rural_urban,
        gini_coefficient=gini,
        concentration_index=conc,
        gender_distribution=gender_dist,
        overall_fairness_score=overall_score,
        recommendations=recommendations,
        raw_metrics={
            "gini": gini,
            "concentration_index": conc,
            "rural_urban": rural_urban,
        },
    )
