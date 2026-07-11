"""
Feature Engineering Module
===========================

Transforms raw candidate and opportunity data into numerical feature
vectors for the ranking models. Includes feature extraction, skill
taxonomy mapping, and text processing.
"""

from .feature_extractor import FeatureExtractor, FeatureVector
from .skill_taxonomy import SkillTaxonomy
from .text_processor import TextProcessor

__all__ = ["FeatureExtractor", "FeatureVector", "SkillTaxonomy", "TextProcessor"]
