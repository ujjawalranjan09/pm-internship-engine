"""Multi-stage matching service: filter → retrieve → rank → explain."""

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.candidate import CandidateProfile
from app.models.match import Match
from app.models.opportunity import Opportunity
from app.services.eligibility_service import EligibilityService
from app.services.fairness_service import FairnessService

logger = logging.getLogger(__name__)
settings = get_settings()


class MatchingService:
    """Orchestrates the multi-stage matching pipeline."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.eligibility_service = EligibilityService()
        self.fairness_service = FairnessService()
        self.weights = settings.MATCH_WEIGHTS

    async def get_recommendations(self, candidate_id: int, top_k: int = 10) -> list[Match]:
        """Get top-K opportunity recommendations for a candidate."""
        # Check for existing matches
        result = await self.db.execute(
            select(Match)
            .where(Match.candidate_id == candidate_id)
            .where(Match.status == "pending")
            .order_by(Match.score.desc())
            .limit(top_k)
        )
        existing = result.scalars().all()
        if existing:
            return list(existing)

        # Generate fresh matches
        candidate_result = await self.db.execute(select(CandidateProfile).where(CandidateProfile.id == candidate_id))
        candidate = candidate_result.scalar_one_or_none()
        if candidate is None:
            return []

        opportunities_result = await self.db.execute(select(Opportunity).where(Opportunity.is_active))
        opportunities = opportunities_result.scalars().all()

        matches = await self._pipeline(candidate, list(opportunities), top_k)
        return matches

    async def run_batch_matching(self) -> dict[str, Any]:
        """Run matching for all active candidates against all active opportunities."""
        candidates_result = await self.db.execute(select(CandidateProfile))
        candidates = candidates_result.scalars().all()

        opportunities_result = await self.db.execute(select(Opportunity).where(Opportunity.is_active))
        opportunities = opportunities_result.scalars().all()

        total_matches = 0
        for candidate in candidates:
            matches = await self._pipeline(candidate, list(opportunities), settings.MATCH_TOP_K)
            total_matches += len(matches)

        return {
            "candidates_processed": len(candidates),
            "opportunities_considered": len(opportunities),
            "total_matches": total_matches,
        }

    async def _pipeline(
        self,
        candidate: CandidateProfile,
        opportunities: list[Opportunity],
        top_k: int,
    ) -> list[Match]:
        """Execute the multi-stage matching pipeline.

        Stage 1: Rule-based eligibility filtering
        Stage 2: Feature-based scoring
        Stage 3: Fairness-aware re-ranking
        Stage 4: Store and return top-K
        """
        # Stage 1: Filter
        eligible = self._filter_stage(candidate, opportunities)
        if not eligible:
            logger.info("No eligible opportunities for candidate %d", candidate.id)
            return []

        # Stage 2: Score
        scored = self._score_stage(candidate, eligible)

        # Stage 3: Fairness re-rank
        if settings.FAIRNESS_ENABLED:
            scored = self.fairness_service.rerank(candidate, scored)

        # Stage 4: Store top-K matches
        top_matches = scored[:top_k]
        stored_matches = await self._store_matches(candidate.id, top_matches)
        return stored_matches

    def _filter_stage(self, candidate: CandidateProfile, opportunities: list[Opportunity]) -> list[Opportunity]:
        """Stage 1: Rule-based eligibility filtering."""
        eligible = []
        for opp in opportunities:
            if self.eligibility_service.is_eligible(candidate, opp):
                eligible.append(opp)
        logger.debug(
            "Filter stage: %d/%d opportunities passed for candidate %d",
            len(eligible),
            len(opportunities),
            candidate.id,
        )
        return eligible

    def _score_stage(
        self, candidate: CandidateProfile, opportunities: list[Opportunity]
    ) -> list[tuple[Opportunity, float, dict[str, float]]]:
        """Stage 2: Feature-based scoring with weighted components."""
        scored: list[tuple[Opportunity, float, dict[str, float]]] = []

        for opp in opportunities:
            breakdown = {
                "skill_similarity": self._skill_similarity(candidate, opp),
                "location_preference": self._location_preference(candidate, opp),
                "education_fit": self._education_fit(candidate, opp),
                "sector_interest": self._sector_interest(candidate, opp),
                "social_equity": self._social_equity(candidate),
                "profile_completeness": candidate.profile_completion_score,
            }

            total_score = sum(self.weights.get(key, 0) * value for key, value in breakdown.items())
            scored.append((opp, total_score, breakdown))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    async def _store_matches(
        self,
        candidate_id: int,
        scored: list[tuple[Opportunity, float, dict[str, float]]],
    ) -> list[Match]:
        """Persist matches to the database."""
        matches = []
        for rank, (opp, score, breakdown) in enumerate(scored, start=1):
            explanation = self._generate_explanation(breakdown)
            match = Match(
                candidate_id=candidate_id,
                opportunity_id=opp.id,
                score=round(score, 4),
                score_breakdown=breakdown,
                explanation=explanation,
                rank=rank,
                status="pending",
            )
            self.db.add(match)
            matches.append(match)

        await self.db.flush()
        for m in matches:
            await self.db.refresh(m)
        return matches

    def _skill_similarity(self, candidate: CandidateProfile, opp: Opportunity) -> float:
        """Compute skill overlap score between candidate and opportunity."""
        candidate_skills = set(s.lower() for s in (candidate.skills or []))
        required_skills = set(s.lower() for s in (opp.required_skills or []))
        if not required_skills:
            return 0.5  # Neutral if no skills specified
        if not candidate_skills:
            return 0.0
        intersection = candidate_skills & required_skills
        return len(intersection) / len(required_skills)

    def _location_preference(self, candidate: CandidateProfile, opp: Opportunity) -> float:
        """Score location match considering mobility preferences."""
        score = 0.5  # Base score

        # Same district = best
        if candidate.district and opp.district and candidate.district.lower() == opp.district.lower():
            score = 1.0
        # Same state = good
        elif candidate.state and opp.state and candidate.state.lower() == opp.state.lower():
            score = 0.8

        # Adjust for mobility preferences
        if candidate.mobility_preferences:
            willing = candidate.mobility_preferences.get("willing_to_relocate", False)
            if willing:
                score = max(score, 0.7)
            remote_ok = candidate.mobility_preferences.get("remote_work_ok", True)
            if remote_ok and opp.work_mode == "remote":
                score = 1.0

        # Remote work is universally accessible
        if opp.work_mode == "remote":
            score = max(score, 0.9)

        return min(score, 1.0)

    def _education_fit(self, candidate: CandidateProfile, opp: Opportunity) -> float:
        """Score education alignment with opportunity requirements."""
        if not candidate.education or not opp.eligibility_criteria:
            return 0.5  # Neutral

        criteria = opp.eligibility_criteria
        edu = candidate.education
        score = 0.5

        # Check minimum education level
        min_edu = criteria.get("min_education")
        if min_edu:
            edu_hierarchy = {"10th": 1, "12th": 2, "diploma": 3, "bachelors": 4, "masters": 5, "phd": 6}
            candidate_level = edu_hierarchy.get(edu.get("degree", "").lower(), 0)
            required_level = edu_hierarchy.get(min_edu.lower(), 0)
            if candidate_level >= required_level:
                score = 1.0
            elif candidate_level >= required_level - 1:
                score = 0.7
            else:
                score = 0.2

        # Check field match
        required_field = criteria.get("field_of_study")
        if (
            required_field
            and edu.get("field_of_study")
            and required_field.lower() in edu.get("field_of_study", "").lower()
        ):
            score = min(score + 0.2, 1.0)

        return score

    def _sector_interest(self, candidate: CandidateProfile, opp: Opportunity) -> float:
        """Score sector alignment based on candidate skills and opportunity sector."""
        if not opp.sector or not candidate.skills:
            return 0.5

        sector_skill_map = {
            "technology": [
                "python",
                "java",
                "javascript",
                "sql",
                "machine learning",
                "data science",
                "web development",
                "cloud",
                "devops",
            ],
            "finance": ["accounting", "finance", "excel", "sql", "data analysis", "banking"],
            "healthcare": ["biology", "chemistry", "healthcare", "medical", "nursing", "pharmacy"],
            "education": ["teaching", "training", "curriculum", "education"],
            "manufacturing": ["mechanical", "electrical", "production", "quality", "manufacturing"],
            "agriculture": ["agriculture", "farming", "horticulture", "agronomy"],
            "marketing": ["marketing", "digital marketing", "seo", "social media", "content writing"],
        }

        sector_lower = opp.sector.lower()
        candidate_skills_lower = [s.lower() for s in candidate.skills]

        relevant_skills = set()
        for sector_key, skills in sector_skill_map.items():
            if sector_key in sector_lower:
                relevant_skills = set(skills)
                break

        if not relevant_skills:
            return 0.5

        overlap = sum(1 for s in candidate_skills_lower if any(r in s for r in relevant_skills))
        return min(overlap / max(len(relevant_skills) * 0.3, 1), 1.0)

    def _social_equity(self, candidate: CandidateProfile) -> float:
        """Score social equity factor for fairness-aware matching."""
        score = 0.5
        if candidate.social_category in ("sc", "st"):
            score = 0.9
        elif candidate.social_category == "obc" or candidate.social_category == "ews":
            score = 0.7
        if candidate.is_rural:
            score = min(score + 0.1, 1.0)
        return score

    def _generate_explanation(self, breakdown: dict[str, float]) -> str:
        """Generate human-readable explanation of match scoring."""
        strengths = []
        gaps = []

        for key, value in breakdown.items():
            label = key.replace("_", " ").title()
            if value >= 0.7:
                strengths.append(f"{label}: {value:.0%}")
            elif value < 0.4:
                gaps.append(f"{label}: {value:.0%}")

        parts = []
        if strengths:
            parts.append(f"Strengths: {', '.join(strengths)}")
        if gaps:
            parts.append(f"Areas for improvement: {', '.join(gaps)}")

        return ". ".join(parts) if parts else "Match score based on overall profile alignment."
