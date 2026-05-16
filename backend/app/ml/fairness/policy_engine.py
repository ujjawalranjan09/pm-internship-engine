"""
Policy Engine – Configurable Fairness Policies
================================================

Applies configurable fairness policies to the allocation process.
Policies are defined as rules with conditions and actions, allowing
administrators to tune fairness behaviour without code changes.

Policy types:
    - Category boost: increase scores for under-represented groups
    - Minimum quota: guarantee minimum representation
    - Geographic diversity: bonus for under-represented districts
    - Gender parity: target-based gender balancing
    - Quality floor: reject matches below minimum score
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class PolicyType(StrEnum):
    """Types of fairness policies."""

    CATEGORY_BOOST = "category_boost"
    MIN_QUOTA = "min_quota"
    GEO_DIVERSITY = "geo_diversity"
    GENDER_PARITY = "gender_parity"
    QUALITY_FLOOR = "quality_floor"
    RURAL_BOOST = "rural_boost"
    CUSTOM = "custom"


class PolicyAction(StrEnum):
    """What a policy does when triggered."""

    BOOST_SCORE = "boost_score"
    REDUCE_SCORE = "reduce_score"
    GUARANTEE_SLOT = "guarantee_slot"
    REJECT = "reject"
    LOG = "log"


@dataclass
class PolicyRule:
    """A single fairness policy rule."""

    name: str
    policy_type: PolicyType
    action: PolicyAction
    enabled: bool = True
    priority: int = 0  # Higher = applied first

    # Conditions
    target_groups: list[str] = field(default_factory=list)
    min_group_size: int = 0  # Minimum candidates in group to activate

    # Parameters
    boost_amount: float = 0.0
    quota_fraction: float = 0.0
    threshold: float = 0.0

    # Custom function (for PolicyType.CUSTOM)
    custom_fn: Callable | None = field(default=None, repr=False)

    def matches(self, candidate_metadata: dict[str, Any]) -> bool:
        """Check if this policy applies to a candidate."""
        if not self.enabled:
            return False

        if not self.target_groups:
            return True

        candidate_group = (candidate_metadata.get("social_category", "general")).lower()

        return candidate_group in [g.lower() for g in self.target_groups]


@dataclass
class PolicyApplication:
    """Result of applying a policy to a single candidate."""

    policy_name: str
    action: PolicyAction
    adjustment: float = 0.0
    reason: str = ""


class PolicyEngine:
    """
    Configurable fairness policy engine.

    Manages a set of PolicyRules and applies them to candidate
    scores during the matching pipeline.

    Usage:
        engine = PolicyEngine()
        engine.add_rule(PolicyRule(...))
        adjusted_score = engine.apply(candidate_metadata, original_score)
    """

    # Default policies for the PM Internship Scheme
    DEFAULT_POLICIES = [
        PolicyRule(
            name="sc_category_boost",
            policy_type=PolicyType.CATEGORY_BOOST,
            action=PolicyAction.BOOST_SCORE,
            target_groups=["sc", "scheduled caste"],
            boost_amount=0.08,
            priority=10,
        ),
        PolicyRule(
            name="st_category_boost",
            policy_type=PolicyType.CATEGORY_BOOST,
            action=PolicyAction.BOOST_SCORE,
            target_groups=["st", "scheduled tribe"],
            boost_amount=0.10,
            priority=10,
        ),
        PolicyRule(
            name="obc_category_boost",
            policy_type=PolicyType.CATEGORY_BOOST,
            action=PolicyAction.BOOST_SCORE,
            target_groups=["obc", "other backward class"],
            boost_amount=0.05,
            priority=10,
        ),
        PolicyRule(
            name="rural_boost",
            policy_type=PolicyType.RURAL_BOOST,
            action=PolicyAction.BOOST_SCORE,
            boost_amount=0.06,
            priority=8,
        ),
        PolicyRule(
            name="gender_parity_boost",
            policy_type=PolicyType.GENDER_PARITY,
            action=PolicyAction.BOOST_SCORE,
            target_groups=["female", "f", "woman"],
            boost_amount=0.03,
            priority=5,
        ),
        PolicyRule(
            name="quality_floor",
            policy_type=PolicyType.QUALITY_FLOOR,
            action=PolicyAction.REJECT,
            threshold=0.15,
            priority=100,
        ),
    ]

    def __init__(
        self,
        rules: list[PolicyRule] | None = None,
        use_defaults: bool = True,
        max_total_boost: float = 0.25,
    ) -> None:
        """
        Initialise the policy engine.

        Args:
            rules: Custom policy rules.
            use_defaults: Whether to include default PM Internship policies.
            max_total_boost: Maximum cumulative boost that can be applied.
        """
        self._rules: list[PolicyRule] = []
        self._max_total_boost = max_total_boost

        if use_defaults:
            self._rules.extend(self.DEFAULT_POLICIES)

        if rules:
            self._rules.extend(rules)

        # Sort by priority descending (highest priority first)
        self._rules.sort(key=lambda r: -r.priority)

        logger.info("PolicyEngine initialized with %d rules", len(self._rules))

    def add_rule(self, rule: PolicyRule) -> None:
        """Add a policy rule."""
        self._rules.append(rule)
        self._rules.sort(key=lambda r: -r.priority)
        logger.info("Added policy rule: %s", rule.name)

    def remove_rule(self, name: str) -> bool:
        """Remove a policy rule by name."""
        before = len(self._rules)
        self._rules = [r for r in self._rules if r.name != name]
        removed = len(self._rules) < before
        if removed:
            logger.info("Removed policy rule: %s", name)
        return removed

    def get_rules(self) -> list[PolicyRule]:
        """Return all active rules."""
        return [r for r in self._rules if r.enabled]

    def apply(
        self,
        candidate_metadata: dict[str, Any],
        original_score: float,
        context: dict[str, Any] | None = None,
    ) -> tuple[float, list[PolicyApplication]]:
        """
        Apply all matching policies to a candidate's score.

        Args:
            candidate_metadata: Dict with social_category, is_rural, gender, etc.
            original_score: The pre-fairness match score.
            context: Additional context (group counts, opportunity info, etc.).

        Returns:
            Tuple of (adjusted_score, list_of_applications).
        """
        ctx = context or {}
        applications: list[PolicyApplication] = []
        total_boost = 0.0
        rejected = False

        for rule in self._rules:
            if not rule.enabled:
                continue

            if not rule.matches(candidate_metadata):
                continue

            # Check minimum group size
            if rule.min_group_size > 0:
                group_count = ctx.get("group_counts", {}).get(
                    candidate_metadata.get("social_category", "general").lower(), 0
                )
                if group_count < rule.min_group_size:
                    continue

            if rule.action == PolicyAction.REJECT:
                if original_score < rule.threshold:
                    rejected = True
                    applications.append(
                        PolicyApplication(
                            policy_name=rule.name,
                            action=rule.action,
                            reason=f"Score {original_score:.3f} below threshold {rule.threshold:.3f}",
                        )
                    )
                    break

            elif rule.action == PolicyAction.BOOST_SCORE:
                if total_boost + rule.boost_amount <= self._max_total_boost:
                    total_boost += rule.boost_amount
                    applications.append(
                        PolicyApplication(
                            policy_name=rule.name,
                            action=rule.action,
                            adjustment=rule.boost_amount,
                            reason=f"{rule.policy_type.value} boost for {rule.target_groups or 'all'}",
                        )
                    )

            elif rule.action == PolicyAction.REDUCE_SCORE:
                reduction = min(rule.boost_amount, original_score + total_boost - 0.01)
                if reduction > 0:
                    total_boost -= reduction
                    applications.append(
                        PolicyApplication(
                            policy_name=rule.name,
                            action=rule.action,
                            adjustment=-reduction,
                            reason=f"{rule.policy_type.value} reduction",
                        )
                    )

            elif rule.action == PolicyAction.GUARANTEE_SLOT:
                applications.append(
                    PolicyApplication(
                        policy_name=rule.name,
                        action=rule.action,
                        reason=f"Quota: {rule.quota_fraction:.1%} minimum",
                    )
                )

            elif rule.custom_fn:
                adjustment = rule.custom_fn(candidate_metadata, original_score, ctx)
                if adjustment != 0:
                    total_boost += adjustment
                    applications.append(
                        PolicyApplication(
                            policy_name=rule.name,
                            action=PolicyAction.BOOST_SCORE if adjustment > 0 else PolicyAction.REDUCE_SCORE,
                            adjustment=adjustment,
                            reason="Custom policy",
                        )
                    )

        if rejected:
            return 0.0, applications

        adjusted = min(1.0, max(0.0, original_score + total_boost))
        return adjusted, applications

    def apply_batch(
        self,
        candidates: list[dict[str, Any]],
        scores: list[float],
        context: dict[str, Any] | None = None,
    ) -> tuple[list[float], list[list[PolicyApplication]]]:
        """Apply policies to a batch of candidates."""
        adjusted_scores = []
        all_applications = []

        for cand, score in zip(candidates, scores, strict=False):
            adjusted, apps = self.apply(cand, score, context)
            adjusted_scores.append(adjusted)
            all_applications.append(apps)

        return adjusted_scores, all_applications

    def evaluate_policies(
        self,
        candidates: list[dict[str, Any]],
        allocations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Evaluate the impact of current policies on allocations.

        Returns a summary of how many candidates were affected
        by each policy and the total score adjustment.
        """
        policy_impact: dict[str, dict[str, Any]] = {}

        for rule in self._rules:
            if not rule.enabled:
                continue

            affected = 0
            total_adjustment = 0.0

            for cand, alloc in zip(candidates, allocations, strict=False):
                if not alloc.get("is_allocated", False):
                    continue
                if rule.matches(cand):
                    affected += 1
                    total_adjustment += rule.boost_amount

            policy_impact[rule.name] = {
                "type": rule.policy_type.value,
                "affected_count": affected,
                "total_adjustment": round(total_adjustment, 4),
                "average_adjustment": round(total_adjustment / affected if affected > 0 else 0.0, 4),
            }

        return policy_impact
