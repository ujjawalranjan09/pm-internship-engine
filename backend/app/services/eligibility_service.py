"""Eligibility service for hard-filter evaluation."""

import logging

from app.models.candidate import CandidateProfile
from app.models.opportunity import Opportunity

logger = logging.getLogger(__name__)


class EligibilityService:
    """Evaluates hard eligibility criteria that candidates must meet.

    These are binary pass/fail checks that happen before scoring.
    A candidate who fails any hard filter is excluded from matching.
    """

    def is_eligible(self, candidate: CandidateProfile, opportunity: Opportunity) -> bool:
        """Check if a candidate meets all hard eligibility criteria for an opportunity.

        Args:
            candidate: The candidate profile to evaluate.
            opportunity: The opportunity with eligibility criteria.

        Returns:
            True if the candidate is eligible, False otherwise.
        """
        criteria = opportunity.eligibility_criteria or {}

        # Check minimum education
        if not self._check_education(candidate, criteria):
            logger.debug(
                "Candidate %d failed education check for opportunity %d",
                candidate.id,
                opportunity.id,
            )
            return False

        # Check state/district restrictions
        if not self._check_location_eligibility(candidate, criteria):
            logger.debug(
                "Candidate %d failed location check for opportunity %d",
                candidate.id,
                opportunity.id,
            )
            return False

        # Check social category restrictions (if any reservation quotas)
        if not self._check_category_eligibility(candidate, criteria):
            logger.debug(
                "Candidate %d failed category check for opportunity %d",
                candidate.id,
                opportunity.id,
            )
            return False

        # Check minimum profile completion
        min_completion = criteria.get("min_profile_completion", 0.0)
        if candidate.profile_completion_score < min_completion:
            logger.debug(
                "Candidate %d profile completion %.2f < %.2f for opportunity %d",
                candidate.id,
                candidate.profile_completion_score,
                min_completion,
                opportunity.id,
            )
            return False

        return True

    def _check_education(self, candidate: CandidateProfile, criteria: dict) -> bool:
        """Check if candidate meets education requirements."""
        min_education = criteria.get("min_education")
        if not min_education:
            return True

        if not candidate.education:
            return False

        edu_hierarchy = {
            "10th": 1,
            "12th": 2,
            "diploma": 3,
            "bachelors": 4,
            "b.tech": 4,
            "b.sc": 4,
            "b.com": 4,
            "b.a": 4,
            "masters": 5,
            "m.tech": 5,
            "m.sc": 5,
            "mba": 5,
            "phd": 6,
        }

        candidate_degree = candidate.education.get("degree", "").lower()
        candidate_level = edu_hierarchy.get(candidate_degree, 0)
        required_level = edu_hierarchy.get(min_education.lower(), 0)

        return candidate_level >= required_level

    def _check_location_eligibility(self, candidate: CandidateProfile, criteria: dict) -> bool:
        """Check if candidate meets location-based eligibility."""
        allowed_states = criteria.get("allowed_states")
        if allowed_states and candidate.state:
            if candidate.state.lower() not in [s.lower() for s in allowed_states]:
                return False

        excluded_states = criteria.get("excluded_states")
        if excluded_states and candidate.state:
            if candidate.state.lower() in [s.lower() for s in excluded_states]:
                return False

        allowed_districts = criteria.get("allowed_districts")
        if allowed_districts and candidate.district:
            if candidate.district.lower() not in [d.lower() for d in allowed_districts]:
                return False

        return True

    def _check_category_eligibility(self, candidate: CandidateProfile, criteria: dict) -> bool:
        """Check if candidate meets social category eligibility."""
        required_categories = criteria.get("required_social_categories")
        if required_categories:
            if not candidate.social_category:
                return False
            if candidate.social_category.lower() not in [c.lower() for c in required_categories]:
                return False

        rural_only = criteria.get("rural_only", False)
        if rural_only and not candidate.is_rural:
            return False

        return True
