"""Applies affirmative action quotas and fairness post-processing."""

import logging
from typing import Any

from app.core.config import get_settings
from app.models.candidate import Candidate
from app.models.match import Match
from app.models.opportunity import Opportunity

logger = logging.getLogger(__name__)
settings = get_settings()


class FairnessService:
    """Enforces representation quotas on ranked match lists."""

    def __init__(
        self,
        rural_quota: float | None = None,
        sc_st_quota: float | None = None,
    ) -> None:
        self.rural_quota = rural_quota or settings.FAIRNESS_QUOTA_RURAL
        self.sc_st_quota = sc_st_quota or settings.FAIRNESS_QUOTA_SC_ST

    def apply_quotas(
        self,
        ranked_candidates: list[Candidate],
        total_seats: int,
    ) -> list[Candidate]:
        """Select candidates respecting rural and SC/ST quotas."""
        rural_seats = int(total_seats * self.rural_quota)
        sc_st_seats = int(total_seats * self.sc_st_quota)
        general_seats = total_seats - rural_seats - sc_st_seats

        rural_bucket: list[Candidate] = []
        sc_st_bucket: list[Candidate] = []
        general_bucket: list[Candidate] = []

        for candidate in ranked_candidates:
            if candidate.is_rural and len(rural_bucket) < rural_seats:
                rural_bucket.append(candidate)
            elif candidate.category in ("SC", "ST") and len(sc_st_bucket) < sc_st_seats:
                sc_st_bucket.append(candidate)
            elif len(general_bucket) < general_seats:
                general_bucket.append(candidate)

        selected = rural_bucket + sc_st_bucket + general_bucket
        logger.info(
            "Quota allocation: rural=%d sc_st=%d general=%d total=%d",
            len(rural_bucket),
            len(sc_st_bucket),
            len(general_bucket),
            len(selected),
        )
        return selected

    def compute_representation(
        self, candidates: list[Candidate]
    ) -> dict[str, Any]:
        total = len(candidates) or 1
        rural_count = sum(1 for c in candidates if c.is_rural)
        sc_st_count = sum(1 for c in candidates if c.category in ("SC", "ST"))
        pwd_count = sum(1 for c in candidates if c.is_pwd)
        return {
            "total": total,
            "rural_pct": rural_count / total,
            "sc_st_pct": sc_st_count / total,
            "pwd_pct": pwd_count / total,
        }
