"""
Match Explainer – Human-Readable Match Explanations
=====================================================

Generates natural-language explanations for why a candidate was
matched to an opportunity. Used for transparency, candidate
communication, and audit trails.

Output format:
    A structured dict with a summary sentence and per-factor
    detail lines, suitable for rendering in a UI or email.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from app.ml.feature_engineering.feature_extractor import FeatureVector

logger = logging.getLogger(__name__)


@dataclass
class MatchExplanation:
    """Structured explanation for a single candidate-opportunity match."""
    summary: str
    factors: List[Dict[str, Any]] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    confidence: str = "medium"  # low, medium, high

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "factors": self.factors,
            "strengths": self.strengths,
            "gaps": self.gaps,
            "confidence": self.confidence,
        }

    def to_text(self) -> str:
        """Plain-text version for notifications."""
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
    """
    Generates human-readable explanations for match scores.

    Examines the feature vector and score breakdown to identify
    the top contributing factors and notable gaps.

    Usage:
        explainer = MatchExplainer()
        explanation = explainer.explain(feature_vector, score, breakdown)
    """

    # Feature names → human-readable labels
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

    # Thresholds for strength/gap detection
    _STRENGTH_THRESHOLD = 0.70
    _GAP_THRESHOLD = 0.30
    _TOP_K_FACTORS = 5

    def explain(
        self,
        features: FeatureVector,
        score: float,
        breakdown: Optional[Dict[str, Any]] = None,
        candidate_name: Optional[str] = None,
        opportunity_title: Optional[str] = None,
    ) -> MatchExplanation:
        """
        Generate a match explanation.

        Args:
            features: The feature vector for this pair.
            score: The final match score (0-1).
            breakdown: Optional score breakdown from the scorer.
            candidate_name: For personalised messages.
            opportunity_title: For personalised messages.

        Returns:
            MatchExplanation with summary, factors, strengths, gaps.
        """
        feat_array = features.to_array()
        feature_names = FeatureVector.feature_names()

        # Build factor list with contributions
        factors = []
        for name, value in zip(feature_names, feat_array):
            label = self._LABELS.get(name, name)
            weight = 0.0
            if breakdown and name in breakdown and isinstance(breakdown[name], dict):
                weight = breakdown[name].get("weight", 0.0)
            contribution = value * weight

            factors.append({
                "feature": name,
                "label": label,
                "value": round(float(value), 3),
                "weight": round(float(weight), 3),
                "contribution": round(float(contribution), 4),
            })

        # Sort by contribution descending
        factors.sort(key=lambda f: -f["contribution"])
        top_factors = factors[: self._TOP_K_FACTORS]

        # Identify strengths and gaps
        strengths = []
        gaps = []
        for f in factors:
            label = f["label"]
            value = f["value"]
            if value >= self._STRENGTH_THRESHOLD:
                strengths.append(f"{label} ({value:.0%})")
            elif value <= self._GAP_THRESHOLD:
                gaps.append(f"{label} ({value:.0%})")

        # Determine confidence
        if score >= 0.75:
            confidence = "high"
        elif score >= 0.45:
            confidence = "medium"
        else:
            confidence = "low"

        # Generate summary
        summary = self._build_summary(
            score, top_factors, strengths, gaps,
            candidate_name, opportunity_title,
        )

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
        top_factors: List[Dict[str, Any]],
        strengths: List[str],
        gaps: List[str],
        candidate_name: Optional[str],
        opportunity_title: Optional[str],
    ) -> str:
        """Build the one-line summary sentence."""
        # Score quality descriptor
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

        # Top factor description
        top_label = top_factors[0]["label"] if top_factors else "overall profile"

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
        features_list: List[FeatureVector],
        scores: List[float],
        breakdowns: Optional[List[Dict[str, Any]]] = None,
    ) -> List[MatchExplanation]:
        """Generate explanations for a batch of matches."""
        explanations = []
        for i, (fv, score) in enumerate(zip(features_list, scores)):
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
        """
        Generate a plain-text email body for notifying a candidate
        about their match.
        """
        lines = [
            f"Dear {candidate_name},",
            "",
            f"We're pleased to inform you that your profile has been matched "
            f"with an internship opportunity: {opportunity_title} at {organisation}.",
            "",
            f"Match Score: {explanation.confidence.title()} ({explanation.summary.split('(')[1].split(')')[0] if '(' in explanation.summary else ''})",
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

        lines.extend([
            "Please log in to your dashboard to review the full details and accept or decline this offer.",
            "",
            "Best regards,",
            "PM Internship Scheme Team",
        ])

        return "\n".join(lines)
