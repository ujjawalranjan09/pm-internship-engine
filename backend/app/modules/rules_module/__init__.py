"""Rules domain module — eligibility criteria and business rules engine."""

import logging
from typing import Any

from app.models.candidate import CandidateProfile
from app.models.opportunity import Opportunity
from app.services.eligibility_service import EligibilityService

logger = logging.getLogger(__name__)


class RulesModule:
    """Domain module for business rules and eligibility evaluation.

    Provides a clean interface over the eligibility service and
    supports custom rule definitions beyond the built-in checks.
    """

    def __init__(self) -> None:
        self._eligibility = EligibilityService()
        self._custom_rules: list[dict[str, Any]] = []

    def is_eligible(self, candidate: CandidateProfile, opportunity: Opportunity) -> bool:
        """Check if a candidate meets all hard eligibility criteria.

        Runs built-in eligibility checks plus any registered custom rules.
        """
        # Built-in checks
        if not self._eligibility.is_eligible(candidate, opportunity):
            return False

        # Custom rules
        for rule in self._custom_rules:
            if not self._evaluate_custom_rule(candidate, opportunity, rule):
                logger.debug(
                    "Candidate %d failed custom rule '%s' for opportunity %d",
                    candidate.id,
                    rule.get("name", "unnamed"),
                    opportunity.id,
                )
                return False

        return True

    def register_rule(self, name: str, rule_fn: Any, description: str = "") -> None:
        """Register a custom eligibility rule.

        Args:
            name: Human-readable rule name.
            rule_fn: Callable(candidate, opportunity) -> bool.
            description: What the rule checks.
        """
        self._custom_rules.append(
            {
                "name": name,
                "fn": rule_fn,
                "description": description,
            }
        )
        logger.info("Registered custom rule: %s", name)

    def get_rules(self) -> list[dict[str, str]]:
        """List all registered rules."""
        return [
            {
                "name": "built-in-eligibility",
                "description": "Education, location, category, and profile completion checks",
            }
        ] + [
            {
                "name": r["name"],
                "description": r.get("description", ""),
            }
            for r in self._custom_rules
        ]

    def filter_eligible(
        self,
        candidate: CandidateProfile,
        opportunities: list[Opportunity],
    ) -> list[Opportunity]:
        """Return only the opportunities a candidate is eligible for."""
        eligible = [o for o in opportunities if self.is_eligible(candidate, o)]
        logger.debug(
            "Eligibility filter: %d/%d passed for candidate %d",
            len(eligible),
            len(opportunities),
            candidate.id,
        )
        return eligible

    @staticmethod
    def _evaluate_custom_rule(
        candidate: CandidateProfile,
        opportunity: Opportunity,
        rule: dict[str, Any],
    ) -> bool:
        """Evaluate a single custom rule."""
        fn = rule.get("fn")
        if fn is None:
            return True
        try:
            return bool(fn(candidate, opportunity))
        except Exception as e:
            logger.warning(
                "Custom rule '%s' raised exception: %s — treating as failed",
                rule.get("name"),
                e,
            )
            return False
