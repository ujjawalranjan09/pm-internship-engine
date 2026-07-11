"""Shared constants for education, sector keywords, and other reusable data."""

from typing import Any

# Education hierarchy - single source of truth
EDUCATION_LEVELS: dict[str, int] = {
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
    "doctorate": 6,
}

# Sector to keywords mapping - single source of truth
SECTOR_KEYWORDS: dict[str, list[str]] = {
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
    "government": ["government", "public", "psu", "ministry", "govt"],
    "consulting": ["consulting", "advisory", "strategy"],
    "media": ["media", "journalism", "content", "publishing", "entertainment"],
    "retail": ["retail", "e-commerce", "ecommerce", "sales"],
}


def get_sector_keywords(sector: str) -> set[str]:
    """Get keywords for a sector."""
    sector_lower = sector.lower()
    for sector_key, keywords in SECTOR_KEYWORDS.items():
        if sector_key in sector_lower:
            return set(keywords)
    return {sector_lower}


def education_match_score(
    candidate_education: dict[str, Any] | None,
    eligibility_criteria: dict[str, Any] | None,
) -> tuple[float, float]:
    """
    Return (qualification_compatibility, education_level_match).
    Both are in [0, 1].
    """
    if not candidate_education or not eligibility_criteria:
        return 0.5, 0.5

    cand_level = candidate_education.get("level", "").lower()
    req_level = eligibility_criteria.get("min_education", "").lower()

    cand_val = EDUCATION_LEVELS.get(cand_level, 3)
    req_val = EDUCATION_LEVELS.get(req_level, 3)

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
    if req_fields and cand_field and any(cand_field in f.lower() or f.lower() in cand_field for f in req_fields):
        qual_compat = min(1.0, qual_compat + 0.15)

    return qual_compat, level_match