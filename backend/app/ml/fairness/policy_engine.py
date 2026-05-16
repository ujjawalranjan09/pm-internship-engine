"""
Fairness Policy Engine – Score Adjustment for Equity
======================================================

Applies configurable fairness policies to raw match scores to promote
equitable outcomes for under-represented groups:

    - Category-based uplift (SC/ST/OBC)
    - Rural preference factor
    - Female candidate uplift
    - Repeat participation penalty
    - District-level representation targets

Policies are configurable via PolicyConfig and applied as additive
adjustments bounded by max_total_adjustment.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class PolicyConfig:
    """Configuration for fairness policy adjustments."""
    district_target_fraction: float = 0.1
    category_balance_factor: float = 0.03
    rural_preference_factor: float = 0.04
    female_target_fraction: float = 0.33
    max_total_adjustment: float = 0.15
    repeat_penalty_per_alloc: float = 0.05
    enable_district_uplift: bool = True
    enable_category_balancing: bool = True
    enable_rural_preference: bool = True
    enable_female_uplift: bool = True
    enable_repeat_penalty: bool = True


def load_policy(config_dict: dict[str, Any]) -> PolicyConfig:
    """Create PolicyConfig from a dict, ignoring unknown keys."""
    import dataclasses as _dc_mod
    valid = {f.name for f in _dc_mod.fields(PolicyConfig)}
    filtered = {k: v for k, v in config_dict.items() if k in valid}
    return PolicyConfig(**filtered)


def apply_policy(
    scores: np.ndarray,
    candidates: Any,
    config: PolicyConfig | None = None,
) -> np.ndarray:
    """Apply fairness policy adjustments to a scores array."""
    cfg = config or PolicyConfig()
    n = len(scores)
    adjusted = scores.copy().astype(float)

    def _col(name: str, default: Any) -> list[Any]:
        if hasattr(candidates, "columns") and name in candidates.columns:
            return list(candidates[name])
        return [default] * n

    categories = _col("category", "general")
    is_rural = _col("is_rural", False)
    genders = _col("gender", "unspecified")
    prev_allocs = _col("previous_allocations", 0)

    category_boosts: dict[str, float] = {
        "sc": 0.08,
        "scheduled caste": 0.08,
        "st": 0.10,
        "scheduled tribe": 0.10,
        "obc": cfg.category_balance_factor,
        "other backward class": cfg.category_balance_factor,
    }

    for i in range(n):
        delta = 0.0
        if cfg.enable_category_balancing:
            delta += category_boosts.get(str(categories[i]).lower(), 0.0)
        if cfg.enable_rural_preference and bool(is_rural[i]):
            delta += cfg.rural_preference_factor
        if cfg.enable_female_uplift and str(genders[i]).lower() in ("female", "f", "woman"):
            delta += 0.03
        if cfg.enable_repeat_penalty:
            n_prev = int(prev_allocs[i]) if prev_allocs[i] else 0
            delta -= n_prev * cfg.repeat_penalty_per_alloc
        delta = max(-float(scores[i]), min(cfg.max_total_adjustment, delta))
        adjusted[i] = max(0.0, scores[i] + delta)
    return adjusted


class PolicyEngine:
    """
    Applies configured fairness policies to a batch of candidate scores.

    Usage:
        engine = PolicyEngine(config)
        adjusted_scores = engine.adjust(raw_scores, candidate_metadata)
    """

    def __init__(self, config: PolicyConfig | None = None) -> None:
        self.config = config or PolicyConfig()

    def adjust(
        self,
        scores: np.ndarray,
        candidate_metadata: list[dict[str, Any]],
    ) -> np.ndarray:
        """Apply all enabled policy rules and return adjusted scores."""
        import pandas as pd
        df = pd.DataFrame(candidate_metadata) if candidate_metadata else pd.DataFrame()
        return apply_policy(scores, df, self.config)

    def explain_adjustments(
        self,
        scores: np.ndarray,
        adjusted_scores: np.ndarray,
        candidate_metadata: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Return per-candidate adjustment explanations."""
        results: list[dict[str, Any]] = []
        for i, meta in enumerate(candidate_metadata):
            if i >= len(scores):
                break
            delta = float(adjusted_scores[i]) - float(scores[i])
            reasons: list[str] = []
            cat = str(meta.get("category", "")).lower()
            if cat in ("sc", "scheduled caste"):
                reasons.append("SC category uplift")
            elif cat in ("st", "scheduled tribe"):
                reasons.append("ST category uplift")
            elif cat in ("obc", "other backward class"):
                reasons.append("OBC category balancing")
            if meta.get("is_rural"):
                reasons.append("Rural preference")
            gender = str(meta.get("gender", "")).lower()
            if gender in ("female", "f", "woman"):
                reasons.append("Female uplift")
            prev = int(meta.get("previous_allocations", 0))
            if prev > 0:
                reasons.append(f"Repeat participation penalty (-{prev} alloc)")
            results.append({
                "candidate_id": meta.get("candidate_id", i),
                "original_score": round(float(scores[i]), 4),
                "adjusted_score": round(float(adjusted_scores[i]), 4),
                "delta": round(delta, 4),
                "reasons": reasons,
            })
        return results
