"""
Match Explainer – Human-Readable Match Explanations
=====================================================

Generates natural-language explanations for why a candidate was
matched to an opportunity. Used for transparency, candidate
communication, and audit trails.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from app.ml.feature_engineering.feature_extractor import FeatureVector

logger = logging.getLogger(__name__)


@dataclass
class MatchExplanation:
    summary: str
    factors: list[dict[str, Any]] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    confidence: str = "medium"

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "factors": self.factors,
            "strengths": self.strengths,
            "gaps": self.gaps,
            "confidence": self.confidence,
        }

    def to_text(self) -> str:
        lines = [self.summary, ""]
        if self.strengths:
            lines.append("Strengths:")
            for s in self.strengths:
                lines.append(f"  ✓ {s}")
        if self.gaps:
            lines.append("Areas to note:")
            for g in self.gaps:
                lines.append(f"  • {g}")
        return "\n".join(lines)


class MatchExplainer:
    _LABELS = {
        "exact_skill_overlap": "Skill match",
        "weighted_skill_similarity": "Skill relevance",
        "qualification_compatibility": "Qualification fit",
        "education_level_match": "Education level",
        "distance_mobility": "Location compatibility",
        "sector_affinity": "Sector alignment",
        "profile_completeness": "Profile completeness",
        "competitiveness_percentile": "Opportunity availability",
        "past_participation": "Prior internship experience",
        "district_representation": "Regional representation",
        "stipend_alignment": "Stipend alignment",
        "semantic_similarity": "Overall profile relevance",
        "text_keyword_overlap": "Keyword match",
    }

    _STRENGTH_THRESHOLD = 0.70
    _GAP_THRESHOLD = 0.30
    _TOP_K_FACTORS = 5

    def explain(
        self,
        features: FeatureVector,
        score: float,
        breakdown: dict[str, Any] | None = None,
        candidate_name: str | None = None,
        opportunity_title: str | None = None,
    ) -> MatchExplanation:
        feat_array = features.to_array()
        feature_names = FeatureVector.feature_names()

        factors: list[dict[str, Any]] = []
        for name, value in zip(feature_names, feat_array, strict=False):
            label = self._LABELS.get(name, name)
            weight = 0.0
            if breakdown and name in breakdown and isinstance(breakdown[name], dict):
                weight = breakdown[name].get("weight", 0.0)
            contribution = value * weight
            factors.append(
                {
                    "feature": name,
                    "label": label,
                    "value": round(float(value), 3),
                    "weight": round(float(weight), 3),
                    "contribution": round(float(contribution), 4),
                }
            )

        factors.sort(key=lambda f: -f["contribution"])
        top_factors = factors[: self._TOP_K_FACTORS]

        strengths = []
        gaps = []
        for f in factors:
            label = f["label"]
            value = f["value"]
            if value >= self._STRENGTH_THRESHOLD:
                strengths.append(f"{label} ({value:.0%})")
            elif value <= self._GAP_THRESHOLD:
                gaps.append(f"{label} ({value:.0%})")

        if score >= 0.75:
            confidence = "high"
        elif score >= 0.45:
            confidence = "medium"
        else:
            confidence = "low"

        summary = self._build_summary(score, top_factors, strengths, gaps, candidate_name, opportunity_title)

        return MatchExplanation(
            summary=summary,
            factors=top_factors,
            strengths=strengths[:5],
            gaps=gaps[:3],
            confidence=confidence,
        )

    def _build_summary(
        self,
        score: float,
        top_factors: list[dict[str, Any]],
        strengths: list[str],
        gaps: list[str],
        candidate_name: str | None,
        opportunity_title: str | None,
    ) -> str:
        if score >= 0.85:
            quality = "excellent"
        elif score >= 0.65:
            quality = "strong"
        elif score >= 0.45:
            quality = "moderate"
        elif score >= 0.25:
            quality = "fair"
        else:
            quality = "limited"

        subject = candidate_name or "The candidate"
        target = opportunity_title or "this opportunity"
        parts = [f"{subject} has a {quality} match ({score:.0%}) with {target}"]
        if top_factors:
            top_factor_str = ", ".join(f["label"].lower() for f in top_factors[:3])
            parts.append(f", driven primarily by {top_factor_str}")
        parts.append(".")
        return "".join(parts)

    def explain_batch(
        self,
        features_list: list[FeatureVector],
        scores: list[float],
        breakdowns: list[dict[str, Any]] | None = None,
    ) -> list[MatchExplanation]:
        explanations = []
        for i, (fv, score) in enumerate(zip(features_list, scores, strict=False)):
            breakdown = breakdowns[i] if breakdowns else None
            explanations.append(self.explain(fv, score, breakdown))
        return explanations

    def generate_email_body(
        self,
        explanation: MatchExplanation,
        candidate_name: str,
        opportunity_title: str,
        organisation: str,
    ) -> str:
        lines = [
            f"Dear {candidate_name},",
            "",
            f"We're pleased to inform you that your profile has been matched "
            f"with an internship opportunity: {opportunity_title} at {organisation}.",
            "",
        ]
        if explanation.strengths:
            lines.append("Why you're a great fit:")
            for s in explanation.strengths:
                lines.append(f"  ✓ {s}")
            lines.append("")
        if explanation.gaps:
            lines.append("Things to keep in mind:")
            for g in explanation.gaps:
                lines.append(f"  • {g}")
            lines.append("")
        lines.extend(
            [
                "Please log in to your dashboard to review the full details.",
                "",
                "Best regards,",
                "PM Internship Scheme Team",
            ]
        )
        return "\n".join(lines)


# ─── Module-level API (required by tests) ────────────────────────────────────


@dataclass
class ScoreBreakdownItem:
    component_name: str
    raw_value: float
    percentage: float
    weight: float = 1.0


@dataclass
class MatchExplanationV2:
    candidate_id: str
    opportunity_id: str
    final_score: float
    score_breakdown: list[ScoreBreakdownItem]
    strengths: list[str]
    gaps: list[str]
    candidate_facing: str
    admin_facing: str
    shap_top_features: list[dict[str, Any]] | None = None


def explain_match(
    candidate: dict[str, Any],
    opportunity: dict[str, Any],
    scores: dict[str, float],
    shap_values: dict[str, float] | None = None,
) -> MatchExplanationV2:
    """Generate structured explanation for a candidate-opportunity match."""
    n = len(scores)
    total_weight = sum(scores.values()) if scores else 1.0
    final_score = min(1.0, total_weight / n) if n > 0 else 0.0
    items: list[ScoreBreakdownItem] = []
    for name, val in scores.items():
        pct = (val / total_weight * 100.0) if total_weight > 0 else 0.0
        items.append(ScoreBreakdownItem(component_name=name, raw_value=val, percentage=round(pct, 2)))
    strengths = [f"{k.replace('_', ' ').title()} ({v:.0%})" for k, v in scores.items() if v >= 0.70]
    gaps = [f"{k.replace('_', ' ').title()} ({v:.0%})" for k, v in scores.items() if v <= 0.30]
    cid = str(candidate.get("candidate_id", ""))
    oid = str(opportunity.get("opportunity_id", ""))
    cname = str(candidate.get("name", "Candidate"))
    title = str(opportunity.get("title", "this opportunity"))
    org = str(opportunity.get("organization", "the organisation"))
    quality = "excellent" if final_score >= 0.85 else "strong" if final_score >= 0.65 else "good"
    cand_text = (
        f"Dear {cname},\n\nYou have a {quality} match ({final_score:.0%}) for {title} at {org}.\n\n"
        "Your profile was evaluated across multiple dimensions:\n"
        + "\n".join(f"  {k.replace('_', ' ').title()}: {v:.0%}" for k, v in scores.items())
        + "\n\nWe encourage you to review the opportunity details on your dashboard."
    )
    admin_text = (
        f"Admin Explanation – Candidate {cid} ({cname})\nOrganisation: {org}\nFinal Score: {final_score:.4f}\n\n"
        "Score Breakdown:\n" + "\n".join(f"  {k}: {v:.4f}" for k, v in scores.items())
    )
    shap_top: list[dict[str, Any]] | None = None
    if shap_values is not None:
        shap_top = [
            {"feature": k, "shap_value": round(v, 4)}
            for k, v in sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)
        ]
    return MatchExplanationV2(
        candidate_id=cid,
        opportunity_id=oid,
        final_score=round(final_score, 4),
        score_breakdown=items,
        strengths=strengths,
        gaps=gaps,
        candidate_facing=cand_text,
        admin_facing=admin_text,
        shap_top_features=shap_top,
    )


def candidate_facing_explanation(explanation: MatchExplanationV2) -> str:
    """Return candidate-facing text from a MatchExplanationV2."""
    return explanation.candidate_facing


def admin_facing_explanation(explanation: MatchExplanationV2) -> str:
    """Return admin-facing text from a MatchExplanationV2."""
    return explanation.admin_facing


def score_breakdown(explanation: MatchExplanationV2) -> list[dict[str, Any]]:
    """Convert breakdown items to list of dicts."""
    return [
        {
            "component_name": i.component_name,
            "raw_value": i.raw_value,
            "percentage": i.percentage,
            "weight": i.weight,
        }
        for i in explanation.score_breakdown
    ]
