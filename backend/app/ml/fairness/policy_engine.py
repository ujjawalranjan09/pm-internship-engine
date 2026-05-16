"""
Configurable policy engine for fairness-aware allocation.
Applies representation targets, category balancing, and preference rules.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class DistrictTarget:
    """Representation target for a district group."""
    district: str
    target_percentage: float  # 0.0 to 1.0
    priority: str = "normal"  # "normal", "aspirational", "high"


@dataclass
class CategoryTarget:
    """Representation target for social category."""
    category: str  # SC, ST, OBC, General
    target_percentage: float
    min_allocation: int = 0


@dataclass
class PolicyConfig:
    """Complete fairness policy configuration."""
    # District representation
    district_targets: list[DistrictTarget] = field(default_factory=list)
    aspirational_district_bonus: float = 0.05
    rural_bonus: float = 0.03

    # Category balancing
    category_targets: list[CategoryTarget] = field(default_factory=list)
    category_balancing_enabled: bool = True
    max_category_adjustment: float = 0.10

    # Gender
    female_participation_target: float = 0.0  # 0 = no target
    female_bonus: float = 0.02

    # Repeat participation
    repeat_participation_penalty: float = 0.05
    max_prior_internships: int = 2

    # Quality guardrails
    min_quality_threshold: float = 0.6
    max_total_adjustment: float = 0.15

    # Geographic spread
    geographic_spread_enabled: bool = True
    max_same_state_percentage: float = 0.40

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PolicyConfig:
        """Create PolicyConfig from a dictionary."""
        config = cls()
        if "district_targets" in data:
            config.district_targets = [
                DistrictTarget(**dt) for dt in data["district_targets"]
            ]
        if "category_targets" in data:
            config.category_targets = [
                CategoryTarget(**ct) for ct in data["category_targets"]
            ]
        for field_name in [
            "aspirational_district_bonus", "rural_bonus",
            "category_balancing_enabled", "max_category_adjustment",
            "female_participation_target", "female_bonus",
            "repeat_participation_penalty", "max_prior_internships",
            "min_quality_threshold", "max_total_adjustment",
            "geographic_spread_enabled", "max_same_state_percentage",
        ]:
            if field_name in data:
                setattr(config, field_name, data[field_name])
        return config

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "district_targets": [
                {"district": dt.district, "target_percentage": dt.target_percentage, "priority": dt.priority}
                for dt in self.district_targets
            ],
            "category_targets": [
                {"category": ct.category, "target_percentage": ct.target_percentage, "min_allocation": ct.min_allocation}
                for ct in self.category_targets
            ],
            "aspirational_district_bonus": self.aspirational_district_bonus,
            "rural_bonus": self.rural_bonus,
            "category_balancing_enabled": self.category_balancing_enabled,
            "max_category_adjustment": self.max_category_adjustment,
            "female_participation_target": self.female_participation_target,
            "female_bonus": self.female_bonus,
            "repeat_participation_penalty": self.repeat_participation_penalty,
            "max_prior_internships": self.max_prior_internships,
            "min_quality_threshold": self.min_quality_threshold,
            "max_total_adjustment": self.max_total_adjustment,
            "geographic_spread_enabled": self.geographic_spread_enabled,
            "max_same_state_percentage": self.max_same_state_percentage,
        }


DEFAULT_POLICY = PolicyConfig(
    aspirational_district_bonus=0.05,
    rural_bonus=0.03,
    category_balancing_enabled=True,
    max_category_adjustment=0.10,
    female_participation_target=0.33,
    female_bonus=0.02,
    repeat_participation_penalty=0.05,
    max_prior_internships=2,
    min_quality_threshold=0.6,
    max_total_adjustment=0.15,
    geographic_spread_enabled=True,
    max_same_state_percentage=0.40,
)


def apply_policy(
    scores: np.ndarray,
    candidates: list[dict[str, Any]],
    policy: PolicyConfig | None = None,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    """
    Apply fairness policy adjustments to match scores.

    Args:
        scores: Original match scores, shape (n_candidates,)
        candidates: List of candidate metadata dicts
        policy: Policy configuration (uses DEFAULT_POLICY if None)

    Returns:
        Tuple of (adjusted_scores, adjustment_log)
    """
    if policy is None:
        policy = DEFAULT_POLICY

    adjusted = scores.copy()
    adjustments_log: list[dict[str, Any]] = []

    for i, candidate in enumerate(candidates):
        original = float(scores[i])
        total_adjustment = 0.0
        reasons: list[str] = []

        # Aspirational district bonus
        if candidate.get("is_aspirational_district", False):
            adj = policy.aspirational_district_bonus
            total_adjustment += adj
            reasons.append(f"aspirational_district +{adj:.3f}")

        # Rural bonus
        if candidate.get("is_rural", False):
            adj = policy.rural_bonus
            total_adjustment += adj
            reasons.append(f"rural +{adj:.3f}")

        # Category balancing
        if policy.category_balancing_enabled:
            category = candidate.get("social_category", "")
            category_target = next(
                (ct for ct in policy.category_targets if ct.category == category), None
            )
            if category_target:
                # Apply a small bonus for underrepresented categories
                adj = min(category_target.target_percentage * 0.05, policy.max_category_adjustment)
                total_adjustment += adj
                reasons.append(f"category_{category} +{adj:.3f}")

        # Female participation
        if policy.female_participation_target > 0 and candidate.get("gender", "").lower() == "female":
            adj = policy.female_bonus
            total_adjustment += adj
            reasons.append(f"female_participation +{adj:.3f}")

        # Repeat participation penalty
        prior_count = candidate.get("prior_internships", 0)
        if prior_count >= policy.max_prior_internships:
            penalty = policy.repeat_participation_penalty * (prior_count - policy.max_prior_internships + 1)
            total_adjustment -= penalty
            reasons.append(f"repeat_penalty -{penalty:.3f}")

        # Cap total adjustment
        total_adjustment = max(-policy.max_total_adjustment, min(policy.max_total_adjustment, total_adjustment))

        # Apply adjustment
        adjusted[i] = original + total_adjustment

        # Quality guardrail: never drop below minimum threshold
        if adjusted[i] < policy.min_quality_threshold:
            adjusted[i] = max(policy.min_quality_threshold, original * 0.9)
            reasons.append("quality_guardrail_applied")

        # Log
        adjustments_log.append({
            "candidate_id": candidate.get("id"),
            "original_score": original,
            "adjustment": total_adjustment,
            "final_score": float(adjusted[i]),
            "reasons": reasons,
        })

    logger.info("Policy applied to %d candidates", len(candidates))
    return adjusted, adjustments_log
