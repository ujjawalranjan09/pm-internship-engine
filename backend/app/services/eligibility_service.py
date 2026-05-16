"""Validates candidate eligibility for a given opportunity."""

import logging
from dataclasses import dataclass, field
from typing import Any

from app.models.candidate import Candidate
from app.models.opportunity import Opportunity

logger = logging.getLogger(__name__)


@dataclass
class EligibilityResult:
    eligible: bool
    reasons: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


class EligibilityService:
    """Checks hard eligibility constraints before scoring."""

    def check(self, candidate: Candidate, opportunity: Opportunity) -> EligibilityResult:
        reasons: list[str] = []
        details: dict[str, Any] = {}

        # Qualification check
        if opportunity.required_qualifications:
            cand_qual = (candidate.highest_qualification or "").lower()
            matched = any(q.lower() in cand_qual for q in opportunity.required_qualifications)
            details["qualification_match"] = matched
            if not matched:
                reasons.append("Qualification does not meet requirements")

        # CGPA check
        if opportunity.min_cgpa is not None and candidate.cgpa is not None:
            if candidate.cgpa < float(opportunity.min_cgpa):
                reasons.append(f"CGPA {candidate.cgpa} below minimum {opportunity.min_cgpa}")
                details["cgpa_check"] = False
            else:
                details["cgpa_check"] = True

        # Capacity check
        capacity_available = opportunity.filled_seats < opportunity.total_seats
        details["capacity_available"] = capacity_available
        if not capacity_available:
            reasons.append("No seats available")

        eligible = len(reasons) == 0
        return EligibilityResult(eligible=eligible, reasons=reasons, details=details)

    def batch_check(
        self,
        candidate: Candidate,
        opportunities: list[Opportunity],
    ) -> list[tuple[Opportunity, EligibilityResult]]:
        """Return (opportunity, result) pairs for all opportunities."""
        return [(opp, self.check(candidate, opp)) for opp in opportunities]
