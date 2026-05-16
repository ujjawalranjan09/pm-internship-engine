"""
Feature Extractor – Candidate-Opportunity Feature Vectors
==========================================================

Converts raw candidate and opportunity data into a fixed-length
numerical feature vector that can be consumed by heuristic scorers
and ML rankers.

Feature groups:
    Skill overlap & similarity
    Qualification compatibility
    Location / distance features
    Sector affinity
    Profile completeness
    Competitiveness signals
    Historical participation
    Text similarity
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class FeatureVector:
    """
    Fixed-length numerical representation of a candidate-opportunity pair.

    All features are normalised to approximately [0, 1] range so that
    the heuristic scorer and ML ranker can combine them without
    additional scaling.
    """

    # ── Skill features ────────────────────────────────────────────
    exact_skill_overlap: float = 0.0       # Jaccard-like overlap ratio
    weighted_skill_similarity: float = 0.0 # Embedding-based similarity

    # ── Qualification features ────────────────────────────────────
    qualification_compatibility: float = 0.0
    education_level_match: float = 0.0

    # ── Location features ─────────────────────────────────────────
    distance_mobility: float = 0.0  # Combined distance + willingness

    # ── Sector features ───────────────────────────────────────────
    sector_affinity: float = 0.0

    # ── Profile features ──────────────────────────────────────────
    profile_completeness: float = 0.0

    # ── Competitiveness ───────────────────────────────────────────
    competitiveness_percentile: float = 0.0

    # ── Historical ────────────────────────────────────────────────
    past_participation: float = 0.0  # 0 = never, 1 = multiple times

    # ── Fairness signals ──────────────────────────────────────────
    district_representation: float = 0.0  # Under-representation score
    stipend_alignment: float = 0.0

    # ── Text / semantic ───────────────────────────────────────────
    semantic_similarity: float = 0.0
    text_keyword_overlap: float = 0.0

    # ── Metadata ──────────────────────────────────────────────────
    metadata: Dict[str, Any] = field(default_factory=dict)

    _FEATURE_NAMES: Optional[List[str]] = None

    @classmethod
    def feature_names(cls) -> List[str]:
        """Return ordered list of feature names matching ``to_array`` order."""
        if cls._FEATURE_NAMES is None:
            cls._FEATURE_NAMES = [
                "exact_skill_overlap",
                "weighted_skill_similarity",
                "qualification_compatibility",
                "distance_mobility",
                "sector_affinity",
                "profile_completeness",
                "competitiveness_percentile",
                "past_participation",
                "district_representation",
                "education_level_match",
                "stipend_alignment",
                "semantic_similarity",
                "text_keyword_overlap",
            ]
        return cls._FEATURE_NAMES

    def to_array(self) -> np.ndarray:
        """Convert to a 1-D numpy array in the canonical feature order."""
        return np.array([
            self.exact_skill_overlap,
            self.weighted_skill_similarity,
            self.qualification_compatibility,
            self.distance_mobility,
            self.sector_affinity,
            self.profile_completeness,
            self.competitiveness_percentile,
            self.past_participation,
            self.district_representation,
            self.education_level_match,
            self.stipend_alignment,
            self.semantic_similarity,
            self.text_keyword_overlap,
        ], dtype=np.float64)

    @classmethod
    def from_array(cls, arr: np.ndarray, metadata: Optional[Dict[str, Any]] = None) -> "FeatureVector":
        """Reconstruct a FeatureVector from a numpy array."""
        names = cls.feature_names()
        if len(arr) != len(names):
            raise ValueError(f"Expected {len(names)} features, got {len(arr)}")
        kwargs: Dict[str, Any] = dict(zip(names, arr.tolist()))
        if metadata:
            kwargs["metadata"] = metadata
        return cls(**kwargs)


# ── Skill-overlap helpers ──────────────────────────────────────────

def _jaccard(a: set, b: set) -> float:
    """Jaccard similarity between two sets."""
    if not a and not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


def _weighted_overlap(
    candidate_skills: List[str],
    required_skills: List[str],
    skill_weights: Optional[Dict[str, float]] = None,
) -> float:
    """
    Weighted skill overlap that gives partial credit for related skills.

    If a skill weight dict is provided, matched skills contribute their
    weight; otherwise each skill contributes equally.
    """
    if not required_skills:
        return 0.0

    weights = skill_weights or {}
    max_weight = max(weights.values()) if weights else 1.0

    candidate_set = {s.lower().strip() for s in candidate_skills}
    total_weight = 0.0
    matched_weight = 0.0

    for skill in required_skills:
        key = skill.lower().strip()
        w = weights.get(key, max_weight * 0.5)
        total_weight += w
        if key in candidate_set:
            matched_weight += w

    return matched_weight / total_weight if total_weight > 0 else 0.0


# ── Distance / location helpers ───────────────────────────────────

# Approximate bounding-box centres for Indian states (lat, lon).
_STATE_CENTRES: Dict[str, Tuple[float, float]] = {
    "andhra pradesh": (15.9129, 79.7400),
    "arunachal pradesh": (28.2180, 94.7278),
    "assam": (26.2006, 92.9376),
    "bihar": (25.0961, 85.3131),
    "chhattisgarh": (21.2787, 81.8661),
    "goa": (15.2993, 74.1240),
    "gujarat": (22.2587, 71.1924),
    "haryana": (29.0588, 76.0856),
    "himachal pradesh": (31.1048, 77.1734),
    "jharkhand": (23.6102, 85.2799),
    "karnataka": (15.3173, 75.7139),
    "kerala": (10.8505, 76.2711),
    "madhya pradesh": (22.9734, 78.6569),
    "maharashtra": (19.7515, 75.7139),
    "manipur": (24.6637, 93.9063),
    "meghalaya": (25.4670, 91.3662),
    "mizoram": (23.1645, 92.9376),
    "nagaland": (26.1584, 94.5624),
    "odisha": (20.9517, 85.0985),
    "punjab": (31.1471, 75.3412),
    "rajasthan": (27.0238, 74.2179),
    "sikkim": (27.5330, 88.5122),
    "tamil nadu": (11.1271, 78.6569),
    "telangana": (18.1124, 79.0193),
    "tripura": (23.9408, 91.9882),
    "uttar pradesh": (26.8467, 80.9462),
    "uttarakhand": (30.0668, 79.0193),
    "west bengal": (22.9868, 87.8550),
    "delhi": (28.7041, 77.1025),
    "jammu and kashmir": (33.7782, 76.5762),
    "ladakh": (34.1526, 77.5771),
}


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine distance in kilometres."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _location_score(
    candidate_state: Optional[str],
    opportunity_state: Optional[str],
    is_rural: bool,
    mobility_prefs: Optional[Dict[str, Any]],
) -> float:
    """
    Compute a location compatibility score in [0, 1].

    1.0 = same district, willing to relocate anywhere.
    Higher scores for closer locations and higher mobility willingness.
    """
    if not candidate_state or not opportunity_state:
        return 0.5  # Unknown → neutral

    cand_centre = _STATE_CENTRES.get(candidate_state.lower())
    opp_centre = _STATE_CENTRES.get(opportunity_state.lower())

    if cand_centre and opp_centre:
        dist_km = _haversine_km(*cand_centre, *opp_centre)
    else:
        dist_km = 0.0 if candidate_state.lower() == opportunity_state.lower() else 1500.0

    # Base score: exponential decay with distance
    distance_score = math.exp(-dist_km / 2000.0)

    # Mobility willingness boost
    willing_to_relocate = True
    if mobility_prefs:
        willing_to_relocate = mobility_prefs.get("willing_to_relocate", True)
        max_distance = mobility_prefs.get("max_distance_km")
        if max_distance and dist_km > max_distance:
            distance_score *= 0.3

    if candidate_state.lower() == opportunity_state.lower():
        distance_score = max(distance_score, 0.8)

    # Rural candidates get a small boost for remote/hybrid roles
    rural_boost = 0.05 if is_rural else 0.0

    return min(1.0, distance_score + rural_boost)


# ── Education helpers ──────────────────────────────────────────────

_EDUCATION_LEVELS = {
    "10th": 1,
    "12th": 2,
    "diploma": 3,
    "bachelor": 4,
    "b.tech": 4,
    "b.e": 4,
    "bsc": 4,
    "bcom": 4,
    "ba": 4,
    "master": 5,
    "m.tech": 5,
    "m.e": 5,
    "msc": 5,
    "mba": 5,
    "ma": 5,
    "phd": 6,
    "doctorate": 6,
}


def _education_match_score(
    candidate_education: Optional[Dict[str, Any]],
    eligibility_criteria: Optional[Dict[str, Any]],
) -> Tuple[float, float]:
    """
    Return (qualification_compatibility, education_level_match).

    Both are in [0, 1].
    """
    if not candidate_education or not eligibility_criteria:
        return 0.5, 0.5

    cand_level = candidate_education.get("level", "").lower()
    req_level = eligibility_criteria.get("min_education", "").lower()

    cand_val = _EDUCATION_LEVELS.get(cand_level, 3)
    req_val = _EDUCATION_LEVELS.get(req_level, 3)

    if cand_val >= req_val:
        qual_compat = 1.0
        level_match = 1.0 - min((cand_val - req_val) * 0.1, 0.3)
    else:
        gap = req_val - cand_val
        qual_compat = max(0.0, 1.0 - gap * 0.3)
        level_match = max(0.0, 1.0 - gap * 0.4)

    # Field-of-study bonus
    cand_field = candidate_education.get("field", "").lower()
    req_fields = eligibility_criteria.get("preferred_fields", [])
    if req_fields and cand_field:
        if any(cand_field in f.lower() or f.lower() in cand_field for f in req_fields):
            qual_compat = min(1.0, qual_compat + 0.15)

    return qual_compat, level_match


# ── Sector affinity ────────────────────────────────────────────────

_SECTOR_KEYWORDS: Dict[str, List[str]] = {
    "technology": ["software", "it", "tech", "digital", "data", "ai", "ml", "cloud"],
    "finance": ["banking", "finance", "fintech", "accounting", "insurance"],
    "healthcare": ["health", "medical", "pharma", "hospital", "clinical"],
    "education": ["education", "teaching", "edtech", "training"],
    "manufacturing": ["manufacturing", "production", "factory", "industrial"],
    "agriculture": ["agriculture", "farming", "agri", "rural"],
    "government": ["government", "public", "psu", "ministry", "govt"],
    "consulting": ["consulting", "advisory", "strategy"],
    "media": ["media", "journalism", "content", "publishing", "entertainment"],
    "retail": ["retail", "e-commerce", "ecommerce", "sales"],
}


def _sector_affinity_score(
    candidate_skills: List[str],
    candidate_education: Optional[Dict[str, Any]],
    opportunity_sector: Optional[str],
) -> float:
    """Score how well the candidate's background aligns with the sector."""
    if not opportunity_sector:
        return 0.5

    sector_lower = opportunity_sector.lower()
    keywords = set()
    for sector_key, kw_list in _SECTOR_KEYWORDS.items():
        if sector_key in sector_lower:
            keywords.update(kw_list)
            break
    if not keywords:
        keywords = {sector_lower}

    skill_text = " ".join(s.lower() for s in candidate_skills)
    if candidate_education:
        skill_text += " " + candidate_education.get("field", "").lower()

    matches = sum(1 for kw in keywords if kw in skill_text)
    return min(1.0, matches / max(len(keywords), 1))


# ── Main Extractor ────────────────────────────────────────────────


class FeatureExtractor:
    """
    Extracts feature vectors for candidate-opportunity pairs.

    Usage:
        extractor = FeatureExtractor()
        fv = extractor.extract(candidate_dict, opportunity_dict)
    """

    def __init__(self, skill_weights: Optional[Dict[str, float]] = None) -> None:
        self._skill_weights = skill_weights

    def extract(
        self,
        candidate: Dict[str, Any],
        opportunity: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> FeatureVector:
        """
        Build a FeatureVector from raw candidate and opportunity dicts.

        Expected keys in *candidate*:
            skills, education, state, district, is_rural,
            mobility_preferences, profile_completion_score,
            social_category, past_allocations (optional list)

        Expected keys in *opportunity*:
            required_skills, eligibility_criteria, sector,
            state, district, stipend, capacity, work_mode
        """
        ctx = context or {}

        cand_skills = candidate.get("skills") or []
        req_skills = opportunity.get("required_skills") or []
        cand_edu = candidate.get("education")
        elig = opportunity.get("eligibility_criteria") or {}

        # ── Skill features ────────────────────────────────────────
        exact_overlap = _jaccard(
            {s.lower() for s in cand_skills},
            {s.lower() for s in req_skills},
        )
        weighted_sim = _weighted_overlap(cand_skills, req_skills, self._skill_weights)

        # ── Education features ────────────────────────────────────
        qual_compat, edu_level = _education_match_score(cand_edu, elig)

        # ── Location features ─────────────────────────────────────
        loc_score = _location_score(
            candidate.get("state"),
            opportunity.get("state"),
            candidate.get("is_rural", False),
            candidate.get("mobility_preferences"),
        )

        # ── Sector affinity ───────────────────────────────────────
        sector_score = _sector_affinity_score(
            cand_skills, cand_edu, opportunity.get("sector")
        )

        # ── Profile completeness ──────────────────────────────────
        profile_score = float(candidate.get("profile_completion_score", 0.5))

        # ── Competitiveness ───────────────────────────────────────
        capacity = opportunity.get("capacity", 1)
        total_applicants = ctx.get("total_applicants", max(capacity * 10, 1))
        competitiveness = min(1.0, capacity / total_applicants)

        # ── Historical participation ──────────────────────────────
        past = candidate.get("past_allocations", [])
        past_score = min(1.0, len(past) * 0.25) if past else 0.0

        # ── District representation ───────────────────────────────
        district_count = ctx.get("district_allocation_count", 0)
        district_total = ctx.get("district_candidate_count", 1)
        district_repr = 1.0 - min(1.0, district_count / max(district_total, 1))

        # ── Stipend alignment ─────────────────────────────────────
        expected_stipend = ctx.get("average_stipend", 10000.0)
        opp_stipend = opportunity.get("stipend") or expected_stipend
        stipend_score = min(1.0, opp_stipend / max(expected_stipend, 1.0))

        # ── Text / semantic features (pre-computed externally) ────
        semantic_sim = ctx.get("semantic_similarity", 0.0)
        keyword_overlap = ctx.get("text_keyword_overlap", exact_overlap)

        return FeatureVector(
            exact_skill_overlap=exact_overlap,
            weighted_skill_similarity=weighted_sim,
            qualification_compatibility=qual_compat,
            education_level_match=edu_level,
            distance_mobility=loc_score,
            sector_affinity=sector_score,
            profile_completeness=profile_score,
            competitiveness_percentile=competitiveness,
            past_participation=past_score,
            district_representation=district_repr,
            stipend_alignment=stipend_score,
            semantic_similarity=semantic_sim,
            text_keyword_overlap=keyword_overlap,
        )

    def extract_batch(
        self,
        candidates: List[Dict[str, Any]],
        opportunities: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> np.ndarray:
        """
        Extract features for all candidate × opportunity pairs.

        Returns a matrix of shape ``(len(candidates), len(opportunities), n_features)``.
        """
        n_features = len(FeatureVector.feature_names())
        matrix = np.zeros((len(candidates), len(opportunities), n_features), dtype=np.float64)

        for i, cand in enumerate(candidates):
            for j, opp in enumerate(opportunities):
                fv = self.extract(cand, opp, context)
                matrix[i, j] = fv.to_array()

        return matrix
